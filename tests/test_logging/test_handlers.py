import os
import time
import logging

from uvicore.logging.handlers import DatedFileHandler, is_dated

# NOTE: uvicore/logging/handlers.py is deliberately stdlib-only, so these are pure
# unit tests - no app1 fixture and no bootstrap needed.


DAY = 86400


def _record(message, created=None, level=logging.INFO):
    record = logging.LogRecord('demo', level, __file__, 1, message, None, None)
    if created is not None:
        # The handler keys the filename off record.created (NOT the wall clock), so
        # setting it here is the whole time-travel seam these tests need.
        record.created = created
    return record


def _handler(pattern, **kwargs):
    handler = DatedFileHandler(pattern, **kwargs)
    handler.setFormatter(logging.Formatter('%(asctime)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    return handler


def _stamp(when, fmt='%Y-%m-%d'):
    return time.strftime(fmt, time.localtime(when))


def test_is_dated():
    assert is_dated('/tmp/%Y-%m-%d_Processor.log') is True
    assert is_dated('/tmp/app1.log') is False


def test_dated_filename_uses_strftime_pattern(tmp_path):
    handler = _handler(str(tmp_path / '%Y-%m-%d_Processor.log'))
    handler.emit(_record('hello'))
    handler.close()

    expected = tmp_path / '{}_Processor.log'.format(_stamp(time.time()))
    assert expected.exists()
    assert 'hello' in expected.read_text()


def test_reopens_on_date_change(tmp_path):
    """A long running process rolls to the next day's file on its own."""
    now = time.time()
    handler = _handler(str(tmp_path / '%Y-%m-%d_Processor.log'))
    handler.emit(_record('day one', created=now))
    handler.emit(_record('day two', created=now + DAY))
    handler.emit(_record('day three', created=now + (DAY * 2)))
    handler.close()

    day1 = tmp_path / '{}_Processor.log'.format(_stamp(now))
    day2 = tmp_path / '{}_Processor.log'.format(_stamp(now + DAY))
    day3 = tmp_path / '{}_Processor.log'.format(_stamp(now + (DAY * 2)))

    assert day1.read_text().strip().endswith('day one')
    assert day2.read_text().strip().endswith('day two')
    assert day3.read_text().strip().endswith('day three')

    # Nothing was ever renamed - no TimedRotatingFileHandler style archives
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted([day1.name, day2.name, day3.name])


def test_timestamps_inside_a_file_match_its_filename(tmp_path):
    """The invariant that makes dated files worth having: every %(asctime)s inside
    2026-07-29_X.log really does start with 2026-07-29.  Only possible because the
    filename is keyed off record.created, not the wall clock at emit time."""
    now = time.time()
    handler = _handler(str(tmp_path / '%Y-%m-%d_Processor.log'))
    for offset in (0, DAY, DAY * 2):
        handler.emit(_record('line', created=now + offset))
    handler.close()

    for path in tmp_path.iterdir():
        date = path.name.split('_')[0]
        for line in path.read_text().splitlines():
            assert line.startswith(date), '{} contains a {} timestamp'.format(path.name, line[:10])


def _count_pattern_strftime(monkeypatch, pattern):
    """Count time.strftime calls made for OUR filename pattern.

    logging.Formatter.formatTime() also calls time.strftime (for %(asctime)s), so
    the count has to be filtered down to the handler's own pattern."""
    import uvicore.logging.handlers as handlers_module

    calls = []
    real_strftime = time.strftime

    def counting_strftime(fmt, *args):
        if fmt == pattern: calls.append(fmt)
        return real_strftime(fmt, *args)

    monkeypatch.setattr(handlers_module.time, 'strftime', counting_strftime)
    return calls


def test_filename_recomputed_at_most_once_per_second(tmp_path, monkeypatch):
    """Perf guarantee: the filename is not rebuilt per record."""
    pattern = str(tmp_path / '%Y-%m-%d_Processor.log')
    handler = _handler(pattern)
    calls = _count_pattern_strftime(monkeypatch, pattern)

    created = time.time()
    for i in range(500):
        handler.emit(_record('line {}'.format(i), created=created))
    handler.close()

    assert len(calls) <= 1, 'filename rebuilt {} times for 500 same-second records'.format(len(calls))


def test_static_pattern_never_calls_strftime(tmp_path, monkeypatch):
    """A pattern with no strftime tokens costs nothing extra at all."""
    pattern = str(tmp_path / 'static.log')
    handler = _handler(pattern)
    assert handler.dated is False
    baseline = handler.baseFilename
    calls = _count_pattern_strftime(monkeypatch, pattern)

    for i in range(10):
        handler.emit(_record('line {}'.format(i), created=time.time() + (DAY * i)))
    handler.close()

    assert calls == []
    assert handler.baseFilename == baseline, 'a static pattern must never change filename'
    assert 'line 9' in (tmp_path / 'static.log').read_text()


def test_creates_missing_directories(tmp_path):
    """The old TimedRotatingFileHandler created no directories - a bad LOG_FILE_PATH
    raised FileNotFoundError mid bootstrap."""
    pattern = str(tmp_path / 'deep' / 'nested' / '%Y' / '%Y-%m-%d_Processor.log')
    handler = _handler(pattern)
    handler.emit(_record('hello'))
    handler.close()

    expected = tmp_path / 'deep' / 'nested' / _stamp(time.time(), '%Y') / '{}_Processor.log'.format(_stamp(time.time()))
    assert expected.exists()
    assert 'hello' in expected.read_text()


def test_append_mode_does_not_truncate(tmp_path):
    """Two handlers on one pattern both keep their lines - the multi process proxy.
    This is what makes dated filenames safe for uvicorn --workers N."""
    pattern = str(tmp_path / '%Y-%m-%d_Processor.log')
    first = _handler(pattern)
    second = _handler(pattern)
    first.emit(_record('from process one'))
    second.emit(_record('from process two'))
    first.emit(_record('one again'))
    first.close()
    second.close()

    content = (tmp_path / '{}_Processor.log'.format(_stamp(time.time()))).read_text()
    assert 'from process one' in content
    assert 'from process two' in content
    assert 'one again' in content


def test_write_mode_is_rejected(tmp_path):
    """A 'w' handler would truncate the day's log on every roll."""
    try:
        DatedFileHandler(str(tmp_path / '%Y-%m-%d.log'), mode='w')
    except ValueError as e:
        assert 'append' in str(e)
    else:
        raise AssertionError('mode="w" should have been rejected')


def test_retention_prunes_old_dated_files(tmp_path):
    """Retention replaces stdlib backupCount, which cannot work with dated names
    because getFilesToDelete() builds its prefix from TODAY's baseFilename."""
    now = time.time()
    old = tmp_path / '2020-01-01_Processor.log'
    older = tmp_path / '2020-01-02_Processor.log'
    for path in (old, older):
        path.write_text('ancient\n')
        os.utime(path, (now - (DAY * 30), now - (DAY * 30)))

    handler = _handler(str(tmp_path / '%Y-%m-%d_Processor.log'), retention=7)
    handler.emit(_record('today'))
    handler.close()

    assert not old.exists()
    assert not older.exists()
    assert (tmp_path / '{}_Processor.log'.format(_stamp(now))).exists()


def test_retention_zero_never_deletes(tmp_path):
    now = time.time()
    old = tmp_path / '2020-01-01_Processor.log'
    old.write_text('ancient\n')
    os.utime(old, (now - (DAY * 999), now - (DAY * 999)))

    handler = _handler(str(tmp_path / '%Y-%m-%d_Processor.log'), retention=0)
    handler.emit(_record('today'))
    handler.close()

    assert old.exists(), 'retention=0 must never delete anything'


def test_retention_only_matches_its_own_pattern(tmp_path):
    """A channel's sweep must never touch another channel's (or anyone's) files."""
    now = time.time()
    others = [
        tmp_path / '2020-01-01_Auditor.log',   # another channel
        tmp_path / 'unrelated.log',            # not ours at all
        tmp_path / '2020-01-01_Processor.txt',  # wrong extension
    ]
    for path in others:
        path.write_text('keep me\n')
        os.utime(path, (now - (DAY * 30), now - (DAY * 30)))

    mine = tmp_path / '2020-01-01_Processor.log'
    mine.write_text('delete me\n')
    os.utime(mine, (now - (DAY * 30), now - (DAY * 30)))

    handler = _handler(str(tmp_path / '%Y-%m-%d_Processor.log'), retention=7)
    handler.emit(_record('today'))
    handler.close()

    assert not mine.exists()
    for path in others:
        assert path.exists(), '{} was wrongly pruned'.format(path.name)


def test_retention_runs_on_roll_not_per_record(tmp_path):
    """The sweep is once-a-day work, not once-a-record work."""
    handler = _handler(str(tmp_path / '%Y-%m-%d_Processor.log'), retention=7)
    calls = []
    handler._prune = lambda: calls.append(1)

    created = time.time()
    for i in range(50):
        handler.emit(_record('line {}'.format(i), created=created))
    assert calls == [], 'prune ran without a roll'

    handler.emit(_record('tomorrow', created=created + DAY))
    assert len(calls) == 1, 'prune should run exactly once per roll'
    handler.close()


def test_emit_never_raises_when_resolve_fails(tmp_path):
    """Logging must never raise into the caller."""
    handler = _handler(str(tmp_path / '%Y-%m-%d_Processor.log'))
    handler.emit(_record('before'))

    errors = []
    handler.handleError = lambda record: errors.append(record)
    handler._resolve = lambda when: (_ for _ in ()).throw(OSError('disk gone'))

    handler.emit(_record('during failure', created=time.time() + DAY))

    assert len(errors) == 1, 'handleError should have been called'
    handler.close()


def test_glob_is_derived_from_the_pattern(tmp_path):
    handler = DatedFileHandler(str(tmp_path / '%Y-%m-%d_Processor.log'))
    assert handler._glob.endswith('*-*-*_Processor.log')
    handler.close()
