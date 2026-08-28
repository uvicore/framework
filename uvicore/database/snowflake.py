"""Snowflake-specific connection resilience.

WHY THIS MODULE EXISTS
----------------------
A Snowflake session holds TWO tokens: a SESSION token (~1h) and a MASTER token (~4h).
The connector renews the first by itself, but NOT the second.  Read
`snowflake/connector/network.py`: on `390112` SESSION_EXPIRED it calls `_renew_session()`,
but on `390114` MASTER_TOKEN_EXPIRED it only sets `connection.expired = True` - and
nothing in the connector ever reads that flag again.  Key-pair auth has no re-auth path
either (`_reauthenticate()` serves the browser / id-token / OAuth authenticators).

So any process that outlives the master token starts failing every query with:

    390114 (08001): Authentication token has expired.  The user must authenticate again.

Two things then go wrong, and BOTH need fixing - the second is the nasty one:

  1. Nothing kept the session alive.  Handled in `Db.configure_connection()`, which now
     defaults the snowflake connect options to `client_session_keep_alive` (a heartbeat
     thread that refreshes the master token before it can expire).

  2. The dead connection POISONS THE POOL FOREVER.  `snowflake-sqlalchemy` defines no
     `is_disconnect()`, so SQLAlchemy classifies 390114 as an ordinary `ProgrammingError`:
     the connection is rolled back and RETURNED TO THE POOL, then handed straight back out
     on the next query.  Every subsequent query fails identically until the PROCESS is
     restarted - an application-level retry loop can never win.  `pool_pre_ping` cannot
     rescue it either: its `SELECT 1` raises that same plain `ProgrammingError`, and
     `sqlalchemy/pool/base.py` only invalidates on a `DisconnectionError`.

     That is what this module fixes, via SQLAlchemy's `handle_error` hook.

WHY handle_error AND NOT A DIALECT SUBCLASS
-------------------------------------------
Teaching `is_disconnect()` to the dialect would mean subclassing `SnowflakeDialect` and
re-registering it under the `snowflake://` entrypoint - hijacking a name the driver owns,
and silently shadowing whatever a future snowflake-sqlalchemy ships.  `handle_error` is
SQLAlchemy's documented, supported extension point for exactly this: the listener may set
`ctx.is_disconnect = True`, and `sqlalchemy/engine/base.py` re-reads it after the handler
chain and then invalidates the connection AND `_invalidate()`s the pool - so every OTHER
pooled connection built on the same dead token is discarded too, not just the one that
happened to raise.

Listeners are attached PER ENGINE (not to the `Engine` class), so a process holding both a
Snowflake and a Postgres connection only pays for it on the Snowflake one, and an engine
rebuilt by a re-init (ex: an app switching snowflake warehouse) is re-armed by `Db.init()`.
"""
import re
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine


# Snowflake GS error codes that mean "this SESSION is dead; a NEW connection is required".
# Names/values from snowflake/connector/network.py.  None of these is retryable ON the
# connection that raised it, which is exactly what makes them disconnects.
#
#   390110  ID_TOKEN_EXPIRED
#   390113  MASTER_TOKEN_NOTFOUND
#   390114  MASTER_TOKEN_EXPIRED    <- the one long-running processes actually hit
#   390115  MASTER_TOKEN_INVALID
#
# DELIBERATELY ABSENT: 390112 SESSION_EXPIRED.  The connector renews that one itself, so
# treating it as a disconnect would throw away a pool that was about to heal on its own.
DEAD_SESSION_CODES = ('390110', '390113', '390114', '390115')

# The connector formats the code ahead of a parenthesised SQLSTATE, e.g.
#   "390114 (08001): None: Authentication token has expired."
# Requiring that '(' is what stops a bound data value that merely CONTAINS the digits from
# tearing down a healthy pool.
_CODE_RE = re.compile(r'\b(' + '|'.join(DEAD_SESSION_CODES) + r')\b\s*\(')

# Marker attribute so a re-arm on an already-armed engine cannot stack duplicate listeners.
_ARMED = '_uvicore_snowflake_session_recovery'


def is_dead_session_error(exception: Any) -> bool:
    """True when `exception` says the Snowflake SESSION is dead (not just the statement)."""
    if exception is None:
        return False

    # Prefer the structured errno the connector sets (an int, ex: 390114) over the message,
    # which is localised/reformatted by every wrapping layer.
    errno = getattr(exception, 'errno', None)
    if errno is not None and str(errno) in DEAD_SESSION_CODES:
        return True

    # SQLAlchemy wraps the DBAPI error; the original is on .orig.
    orig = getattr(exception, 'orig', None)
    if orig is not None and orig is not exception:
        errno = getattr(orig, 'errno', None)
        if errno is not None and str(errno) in DEAD_SESSION_CODES:
            return True

    return bool(_CODE_RE.search(str(exception)))


def register_dead_session_recovery(engine: Engine | AsyncEngine) -> bool:
    """Teach `engine` that a dead Snowflake session is a DISCONNECT, not a query error.

    Returns True if the listener was attached, False if this engine was already armed.
    Idempotent, so `Db.init()` can call it unconditionally on every engine it builds."""

    # An AsyncEngine is a facade; events live on the sync engine underneath.  Snowflake has
    # no async driver today (so this is always the sync branch), but do not encode that
    # assumption - a future asyncio snowflake driver would silently skip the fix.
    target = engine.sync_engine if isinstance(engine, AsyncEngine) else engine

    if getattr(target, _ARMED, False):
        return False
    setattr(target, _ARMED, True)

    @event.listens_for(target, 'handle_error')
    def _dead_session_is_a_disconnect(ctx):
        # Already classified as a disconnect - nothing to add, and skip the string work.
        if ctx.is_disconnect:
            return
        if not is_dead_session_error(ctx.original_exception):
            return

        # THE fix.  engine/base.py re-reads ctx.is_disconnect after this chain and, seeing
        # it flipped, invalidates this connection and the rest of the pool, so the next
        # checkout authenticates from scratch.  The failing statement STILL raises - that
        # is correct and intentional: the caller (or its retry loop) decides what to do,
        # and it now gets a working connection when it tries again.
        ctx.is_disconnect = True

        import uvicore
        uvicore.log.warning(
            'Snowflake session token is dead (code in {}); invalidating the connection '
            'pool so the next query re-authenticates.  The current statement still fails '
            'and should be retried.'.format(', '.join(DEAD_SESSION_CODES))
        )

    return True
