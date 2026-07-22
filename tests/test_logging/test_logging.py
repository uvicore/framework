import io
import pytest
import uvicore
from uvicore.support.dumper import dump
import logging

from rich.rule import Rule
from rich.text import Text
from rich.console import Console

# NOTE: uvicore.logging.logger cannot be imported at module import time because
# its @uvicore.service decorator resolves config during bootstrap.  The app1
# fixture bootstraps uvicore, so import it lazily inside the tests/helpers.


@pytest.mark.asyncio
async def test_logging_module_importable(app1):
    """Test that logging module can be imported"""
    from uvicore import logging as uvicore_logging
    assert uvicore_logging is not None


@pytest.mark.asyncio
async def test_python_logging_integration(app1):
    """Test that logging integrates with Python logging"""
    logger = logging.getLogger('test')
    assert logger is not None
    assert logger.name == 'test'


@pytest.mark.asyncio
async def test_console_handler_is_rich(app1):
    """app1 uses colored console output, so the console handler is rich powered."""
    from uvicore.logging.logger import RichConsoleHandler
    assert isinstance(uvicore.log.console_handler, RichConsoleHandler)


def _record(level, message):
    return logging.LogRecord('demo', level, __file__, 1, message, None, None)


def _handler():
    """A RichConsoleHandler whose stdout/stderr are captured to StringIO."""
    from uvicore.logging.logger import RichConsoleHandler, UVICORE_LOG_THEME
    handler = RichConsoleHandler(colors=True)
    handler.setFormatter(logging.Formatter('%(message)s'))
    handler._stdout_buf = io.StringIO()
    handler._stderr_buf = io.StringIO()
    # no_color so we assert on plain text content, not ANSI codes
    handler._stdout = Console(theme=UVICORE_LOG_THEME, file=handler._stdout_buf, force_terminal=False, no_color=True, width=120, markup=False, highlight=False, emoji=False)
    handler._stderr = Console(theme=UVICORE_LOG_THEME, file=handler._stderr_buf, force_terminal=False, no_color=True, width=120, markup=False, highlight=False, emoji=False)
    return handler


@pytest.mark.asyncio
async def test_render_headers_are_rules(app1):
    """header() and header2() render as full-width rules, header3/4 as inline text."""
    handler = _handler()
    assert isinstance(handler._render(_record(logging.INFO, ':: Section ::')), Rule)
    assert isinstance(handler._render(_record(logging.INFO, '## Sub ##')), Rule)
    assert isinstance(handler._render(_record(logging.INFO, '=== Three ===')), Text)
    assert isinstance(handler._render(_record(logging.INFO, '---- Four ----')), Text)


@pytest.mark.asyncio
async def test_render_separator_and_line_are_rules(app1):
    handler = _handler()
    assert isinstance(handler._render(_record(logging.INFO, '=' * 80)), Rule)
    assert isinstance(handler._render(_record(logging.INFO, '-' * 80)), Rule)


@pytest.mark.asyncio
async def test_render_items_use_glyphs(app1):
    """Item tiers render their configured glyph and preserve indentation."""
    handler = _handler()
    assert '●' in handler._render(_record(logging.INFO, '* one')).plain
    assert '◆' in handler._render(_record(logging.INFO, '    - two')).plain
    assert '✚' in handler._render(_record(logging.INFO, '    + three')).plain
    assert '▸' in handler._render(_record(logging.INFO, '        > four')).plain
    # Indentation is preserved
    assert handler._render(_record(logging.INFO, '    - two')).plain.startswith('    ')


@pytest.mark.asyncio
async def test_render_notice_has_label(app1):
    """NOTICE is a real log level (25) - the label is keyed off the level, not a
    text prefix, so the file handler's levelname column shows NOTICE too."""
    from uvicore.logging.logger import NOTICE
    handler = _handler()
    rendered = handler._render(_record(NOTICE, 'hello')).plain
    assert 'NOTICE' in rendered
    assert 'hello' in rendered


@pytest.mark.asyncio
async def test_notice_uses_real_notice_level(app1):
    """log.notice() emits a record at the custom NOTICE level (not INFO), so the
    plain file handler renders NOTICE in its %(levelname)s column."""
    import logging as _logging
    from uvicore.logging.logger import NOTICE
    assert _logging.getLevelName(NOTICE) == 'NOTICE'

    records = []
    class _Capture(_logging.Handler):
        def emit(self, record): records.append(record)
    capture = _Capture()
    root = _logging.getLogger()
    saved_level = root.level
    root.addHandler(capture)
    # pytest's logging plugin can raise the root level above NOTICE (25); pin it
    # to DEBUG so the record reaches our capture handler.
    root.setLevel(_logging.DEBUG)
    try:
        uvicore.log.notice('a notice message')
    finally:
        root.removeHandler(capture)
        root.setLevel(saved_level)

    notice_records = [r for r in records if r.getMessage() == 'a notice message']
    assert notice_records, 'notice() did not emit a record'
    assert notice_records[0].levelname == 'NOTICE'
    assert notice_records[0].levelno == NOTICE


@pytest.mark.asyncio
async def test_debug_and_info_go_to_stdout(app1):
    handler = _handler()
    handler.emit(_record(logging.DEBUG, 'a debug line'))
    handler.emit(_record(logging.INFO, 'an info line'))
    assert 'a debug line' in handler._stdout_buf.getvalue()
    assert 'an info line' in handler._stdout_buf.getvalue()
    assert handler._stderr_buf.getvalue() == ''


@pytest.mark.asyncio
async def test_warning_error_critical_go_to_stderr(app1):
    handler = _handler()
    handler.emit(_record(logging.WARNING, 'a warning'))
    handler.emit(_record(logging.ERROR, 'an error'))
    handler.emit(_record(logging.CRITICAL, 'a critical'))
    err = handler._stderr_buf.getvalue()
    assert 'a warning' in err
    assert 'an error' in err
    assert 'a critical' in err
    assert handler._stdout_buf.getvalue() == ''


@pytest.mark.asyncio
async def test_colors_false_uses_plain_stream_handler(app1):
    """With colors disabled the handler falls back to a plain StreamHandler."""
    from uvicore.logging.logger import RichConsoleHandler
    # The @uvicore.service decorator replaces the module-level Logger symbol, so
    # grab the real class off the live singleton instead of importing it.
    LoggerClass = type(uvicore.log)
    logger = LoggerClass({'console': {'enabled': True, 'colors': False}, 'file': {'enabled': False}})
    assert isinstance(logger.console_handler, logging.StreamHandler)
    assert not isinstance(logger.console_handler, RichConsoleHandler)
    # Clean up the root logger handlers this ad-hoc Logger added
    root = logging.getLogger()
    root.handlers = [h for h in root.handlers if h is not logger.console_handler]
