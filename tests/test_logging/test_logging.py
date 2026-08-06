import io
import time
import asyncio
import pytest
import uvicore
from uvicore.support.dumper import dump
import logging
import logging.handlers
from contextlib import contextmanager

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
    with isolated_logger({'console': {'enabled': True, 'colors': False}, 'file': {'enabled': False}}) as logger:
        assert isinstance(logger.console_handler, logging.StreamHandler)
        assert not isinstance(logger.console_handler, RichConsoleHandler)


@contextmanager
def isolated_logger(config):
    """Build an ad-hoc Logger without leaking handlers onto the real root logger.

    logging.getLogger() returns a process wide singleton, so a Logger built here
    attaches its handlers to the SAME root logger every other test uses.  Restore
    the handler list (and level) afterwards or the leak compounds across the suite.
    """
    # The @uvicore.service decorator replaces the module-level Logger symbol, so
    # grab the real class off the live singleton instead of importing it.
    LoggerClass = type(uvicore.log)
    root = logging.getLogger()
    saved_handlers, saved_level = list(root.handlers), root.level
    logger = LoggerClass(config)
    try:
        yield logger
    finally:
        for handler in list(root.handlers):
            if handler not in saved_handlers:
                root.removeHandler(handler)
                try: handler.close()
                except Exception: pass
        root.handlers, root.level = saved_handlers, saved_level


@pytest.mark.asyncio
async def test_legacy_config_shape_still_works(app1):
    """The two-key console/file config predates channels and must keep working
    byte for byte - there is no migration."""
    with isolated_logger({
        'console': {'enabled': True, 'level': 'INFO', 'colors': True},
        'file': {'enabled': False},
    }) as logger:
        # Missing keys were deep filled from DEFAULT_CONFIG
        assert logger.config.console.format == '%(message)s'
        assert logger.config.file.when == 'midnight'
        assert logger.config.file.backup_count == 7
        # channels is simply empty
        assert logger.config.channels == {}
        assert logger.channels == {}


@pytest.mark.asyncio
async def test_config_defaults_are_deep_merged(app1, tmp_path):
    """A partial section still gets every default key, unlike the old shallow splat."""
    with isolated_logger({
        'console': {'enabled': False},
        'file': {'enabled': True, 'file': str(tmp_path / 'partial.log')},
    }) as logger:
        assert logger.config.file.level == 'DEBUG'
        assert logger.config.file.retention == 0
        assert 'levelname' in logger.config.file.format
        assert logger.config.file.filters == []


@pytest.mark.asyncio
async def test_defaults_merge_does_not_mutate_the_app_config(app1):
    """Regression: Dict holds nested SuperDicts by reference and defaults() mutates
    in place, so building a Logger without .clone() would rewrite the LIVE
    uvicore.config.app.logger."""
    before = uvicore.config('app.logger').clone()
    with isolated_logger(uvicore.config('app.logger')):
        pass
    assert uvicore.config('app.logger') == before


@pytest.mark.asyncio
async def test_static_file_path_uses_timed_rotating_handler(app1, tmp_path):
    """Backward compatibility: a plain filename keeps the legacy rotation handler."""
    with isolated_logger({
        'console': {'enabled': False},
        'file': {'enabled': True, 'file': str(tmp_path / 'app1.log')},
    }) as logger:
        assert isinstance(logger.file_handler, logging.handlers.TimedRotatingFileHandler)


@pytest.mark.asyncio
async def test_strftime_file_path_uses_dated_handler(app1, tmp_path):
    """A path with strftime tokens selects the dated handler instead."""
    from uvicore.logging.handlers import DatedFileHandler
    with isolated_logger({
        'console': {'enabled': False},
        'file': {'enabled': True, 'file': str(tmp_path / '%Y-%m-%d_app1.log'), 'retention': 14},
    }) as logger:
        assert isinstance(logger.file_handler, DatedFileHandler)
        assert not isinstance(logger.file_handler, logging.handlers.TimedRotatingFileHandler)
        assert logger.file_handler.retention == 14


@pytest.mark.asyncio
async def test_channel_token_resolves_to_default_for_the_main_log(app1, tmp_path):
    """{channel} lets one configured path serve the default log and every channel."""
    with isolated_logger({
        'console': {'enabled': False},
        'file': {'enabled': True, 'file': str(tmp_path / '%Y-%m-%d_{channel}.log')},
    }) as logger:
        logger.info('a default line')
        expected = tmp_path / '{}_default.log'.format(time.strftime('%Y-%m-%d', time.localtime()))
        assert expected.exists()
        assert 'a default line' in expected.read_text()


@pytest.mark.asyncio
async def test_name_scope_is_task_local(app1):
    """uvicore.log is a singleton in an async framework.  The one-shot name() scope
    lives in a ContextVar so two concurrent tasks cannot clobber each other between
    the name() call and the emit."""
    seen = {}

    async def scoped():
        uvicore.log.name('uvicore.orm')
        await asyncio.sleep(0)
        seen['scoped'] = uvicore.log.logger.name
        uvicore.log.reset()

    async def unscoped():
        await asyncio.sleep(0)
        seen['unscoped'] = uvicore.log.logger.name

    await asyncio.gather(scoped(), unscoped())

    assert seen['scoped'] == 'uvicore.orm'
    assert seen['unscoped'] == 'root', 'the other task leaked its logger scope'


@pytest.mark.asyncio
async def test_name_scope_is_cleared_after_one_emit(app1):
    uvicore.log.name('uvicore.orm')
    assert uvicore.log.logger.name == 'uvicore.orm'
    uvicore.log.info('scoped message')
    assert uvicore.log.logger.name == 'root'


@pytest.mark.asyncio
async def test_dump_uses_the_logger_name(app1, tmp_path):
    """dump() reads self.logger.name, which covers root, a name()d scope and a
    channel with one expression."""
    with isolated_logger({
        'console': {'enabled': False},
        'file': {'enabled': True, 'level': 'DEBUG', 'file': str(tmp_path / 'dump.log')},
    }) as logger:
        logger.dump({'answer': 42})
        assert 'answer' in (tmp_path / 'dump.log').read_text()
