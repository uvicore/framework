from __future__ import annotations

import os
import re
import glob
import time
import logging

# NOTE: This module is deliberately stdlib-only (no uvicore imports).  It must be
# importable and unit testable without bootstrapping an application.


# Matches a single strftime conversion token (%Y, %-d, %03H, %%, ...) so a dated
# pattern can be turned into a shell glob for the retention sweep.
STRFTIME_TOKEN = re.compile(r'%[-_0^#]?\d*[a-zA-Z%]')


def is_dated(pattern: str) -> bool:
    """Does this filename pattern contain strftime tokens (and so vary by date)?"""
    return '%' in pattern


class DatedFileHandler(logging.FileHandler):
    """A file handler that builds the date INTO the filename instead of rotating.

    Give it an strftime pattern such as '/var/log/acme/%Y-%m-%d_Processor.log' and
    it writes to '/var/log/acme/2026-07-29_Processor.log', reopening on the new
    day's file automatically when the date changes.  A long running process (an
    infinite loop redis/kafka consumer, a queue worker) therefore rolls to the
    next day's file on its own.

    Why not TimedRotatingFileHandler?  That handler *renames* files on rollover,
    which has two real problems:

    1. Idle across a boundary and the archive is named after the interval that
       *should* have ended, not the data inside it.  A process idle Mon->Thu
       produces one file named for Monday containing Mon+Tue+Wed data, and no
       files at all for Tue/Wed.

    2. Multiple processes on one filename (uvicorn --workers N, a CLI command
       running alongside the server) race on the rename.  One process renames the
       file out from under the others, and the loser's doRollover() takes the
       'already rolled over' early return WITHOUT updating its rolloverAt - so it
       never rotates again and keeps appending to a renamed (or backupCount
       deleted) inode for the rest of its life.  Silent, permanent data loss.

    Because this handler never renames anything, every process independently
    derives the same wall-clock filename and opens it 'a'.  There is nothing to
    coordinate and nothing to race on.

    Notes and deliberate trade-offs:

    - The date comes from ``record.created``, not from the wall clock at emit
      time.  logging.Formatter renders %(asctime)s from record.created too, so
      this preserves the whole point of dated files: every timestamp inside
      2026-07-29_Processor.log really does start with 2026-07-29.

    - Rolling is forward only.  A record created just before midnight but emitted
      after it lands in the newer file.  Mapping every record to its own day's
      file would be more precise but lets a stepping clock thrash the handler
      open and closed, so it is not done.

    - The filename is recomputed at most once per wall-clock second, so a date
      change can be noticed up to a second late.  A pattern with no strftime
      tokens never calls strftime at all.

    - mode is always append.  Nothing is ever renamed or truncated, so N
      processes can share one file: O_APPEND makes each write(2) atomic, so
      lines do not interleave.  A record larger than the ~8KB stream buffer can
      be split across writes though (uvicore logs whole SQL statements and
      dump()s dicts, so this is reachable) - put a {pid} in the filename if you
      need a hard guarantee.

    - Dated filenames trade the rename race for a permissions race: if two
      different UIDs append to the same dated file the second gets EACCES on
      every record.  Use a shared group, or a per-process filename.

    - ``retention`` (in days, 0 = keep forever) deletes old files matching this
      handler's own pattern.  It is NOT the stdlib backupCount: that mechanism
      cannot work with dated filenames because getFilesToDelete() builds its
      prefix from today's baseFilename, so yesterday's files never match it.
      The sweep runs when the file rolls (about once a day), never per record.
      For compression, size caps or offsite shipping use logrotate instead.
    """

    def __init__(
        self,
        pattern: str,
        *,
        mode: str = 'a',
        encoding: str | None = 'utf-8',
        delay: bool = False,
        errors: str | None = None,
        utc: bool = False,
        retention: int = 0,
    ) -> None:
        if 'a' not in mode:
            # A 'w' handler truncates on every reopen, which would destroy the
            # day's log the first time it rolled, and is dead after close().
            raise ValueError("DatedFileHandler requires an append mode, got {}".format(mode))

        self._pattern = os.fspath(pattern)
        self._dated = is_dated(self._pattern)
        self._glob = self._build_glob(self._pattern) if self._dated else None
        self.utc = utc
        self.retention = int(retention or 0)

        # -1 is never a valid int(record.created), so the first emit always checks
        self._checked_at = -1

        filename = self._resolve(time.time())
        self._checked_at = int(time.time())
        super().__init__(filename, mode=mode, encoding=encoding, delay=delay, errors=errors)
        self._prune()

    @property
    def pattern(self) -> str:
        """The configured strftime filename pattern"""
        return self._pattern

    @property
    def dated(self) -> bool:
        """Does the pattern actually vary by date?"""
        return self._dated

    def emit(self, record: logging.LogRecord) -> None:
        """Switch to the record's dated file if needed, then write it.

        The check is hooked here rather than in _open() because _open() only runs
        once per stream lifetime - a filename computed there would never change in
        the long running process this handler exists for.
        """
        if self._dated:
            try:
                # Cheap guard: the filename can only change when the wall clock
                # second changes, so this costs two int compares per record and
                # calls strftime at most once a second.
                created = int(record.created)
                if created != self._checked_at:
                    # Stamp first so a failure below cannot spin on every record
                    self._checked_at = created
                    filename = self._resolve(record.created)
                    if filename != self.baseFilename:
                        self._reopen(filename)
            except Exception:
                # Logging must never raise into the caller.  Fall through and let
                # FileHandler.emit try - it reports via handleError() too.
                self.handleError(record)
        super().emit(record)

    def _resolve(self, when: float) -> str:
        """Build the absolute filename for a moment in time, creating its directory"""
        if self._dated:
            timetuple = time.gmtime(when) if self.utc else time.localtime(when)
            filename = time.strftime(self._pattern, timetuple)
        else:
            filename = self._pattern
        filename = os.path.abspath(filename)

        # Done on every resolve, not just in __init__, because a pattern can
        # include dated directories (%Y/%m/) and because an operator can delete
        # the log directory under a running process.  exist_ok makes the race
        # between multiple processes harmless.
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        return filename

    def _reopen(self, filename: str) -> None:
        """Close the current file and open a different one"""
        # self.lock is an RLock already held by Handler.handle(), so re-entering
        # is free.  Taken explicitly because emit() can also be called directly,
        # bypassing handle().  NEVER take the module level logging._lock here -
        # FileHandler.close() takes self.lock then that one, so doing the reverse
        # would deadlock.
        with self.lock:
            if self.stream:
                # Clear the stream BEFORE closing so a later failure can never
                # leave a closed-but-still-referenced stream behind.
                stream, self.stream = self.stream, None
                try:
                    stream.flush()
                finally:
                    stream.close()
            self.baseFilename = filename
            if not self.delay:
                self.stream = self._open()
        self._prune()

    def _prune(self) -> None:
        """Delete files older than retention days matching this handler's pattern"""
        if not self.retention or not self._glob:
            return
        cutoff = time.time() - (self.retention * 86400)
        try:
            paths = glob.glob(self._glob)
        except OSError:
            return
        for path in paths:
            try:
                if os.path.abspath(path) == self.baseFilename:
                    continue
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except OSError:
                # Another process may have removed it already, or it may not be
                # ours to delete.  Never raise from the logging path.
                pass

    @staticmethod
    def _build_glob(pattern: str) -> str:
        """Turn a dated pattern into a glob so retention only sees its OWN files

        '/var/log/%Y-%m-%d_Processor.log' -> '/var/log/*_Processor.log', which
        cannot match another channel's files.
        """
        return re.sub(r'\*{2,}', '*', STRFTIME_TOKEN.sub('*', pattern))
