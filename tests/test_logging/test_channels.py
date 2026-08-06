import io
import time
import asyncio
import logging
import pytest
import uvicore
from contextlib import contextmanager

from rich.console import Console

# NOTE: uvicore.logging.logger cannot be imported at module import time because its
# @uvicore.service decorator resolves config during bootstrap.  The app1 fixture
# bootstraps uvicore, so import it lazily inside the tests/helpers.

DAY = 86400


@contextmanager
def isolated_logger(config):
    """Build an ad-hoc Logger without leaking handlers onto the real root logger.

    logging.getLogger() returns a process wide singleton, so a Logger built here
    attaches its handlers to the SAME root logger every other test uses.  Restore
    the handler list (and level) afterwards or the leak compounds across the suite.
    """
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
        # logging.Logger.manager.loggerDict never shrinks, so channel loggers
        # outlive this test.  Strip what we attached to them.
        for channel in logger.channels.values():
            for handler in list(channel.logger.handlers):
                channel.logger.removeHandler(handler)
                try: handler.close()
                except Exception: pass
            channel.logger.propagate = True


def _config(tmp_path, channels=None, **file_overrides):
    """A Logger config writing dated files under tmp_path, console off by default."""
    file_config = {
        'enabled': True,
        'level': 'DEBUG',
        'file': str(tmp_path / '%Y-%m-%d_{channel}.log'),
    }
    file_config.update(file_overrides)
    return {
        'console': {'enabled': False},
        'file': file_config,
        'channels': channels or {},
    }


def _today(tmp_path, channel):
    return tmp_path / '{}_{}.log'.format(time.strftime('%Y-%m-%d', time.localtime()), channel)


@pytest.mark.asyncio
async def test_channel_is_cached_and_registered(app1, tmp_path):
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        first = log.channel('Processor')
        assert first is log.channel('Processor'), 'channels must be cached'
        assert 'Processor' in log.channels
        assert log.channels['Processor'] is first


@pytest.mark.asyncio
async def test_channel_has_its_own_python_logger(app1, tmp_path):
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        channel = log.channel('Processor')
        assert channel.channel == 'Processor'
        assert channel.logger.name == 'Processor'
        # propagate=False is what stops channel records reaching the root file handler
        assert channel.logger.propagate is False


@pytest.mark.asyncio
async def test_each_channel_writes_to_its_own_dated_file(app1, tmp_path):
    """The headline requirement: one app, many logs, date in the filename."""
    names = ['Auditor', 'Importer', 'Processor', 'RulesEngine', 'Transformer']
    with isolated_logger(_config(tmp_path, {name: {} for name in names})) as log:
        for name in names:
            log.channel(name).info('hello from {}'.format(name))

        for name in names:
            path = _today(tmp_path, name)
            assert path.exists(), '{} was not created'.format(path.name)
            assert 'hello from {}'.format(name) in path.read_text()


@pytest.mark.asyncio
async def test_channel_does_not_write_to_the_default_file(app1, tmp_path):
    """The crux of the propagate=False design - no double writes."""
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        log.channel('Processor').info('channel only line')
        assert 'channel only line' not in _today(tmp_path, 'default').read_text()


@pytest.mark.asyncio
async def test_default_logger_does_not_write_to_a_channel_file(app1, tmp_path):
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        log.channel('Processor').info('prime the channel file')
        log.info('default only line')

        assert 'default only line' in _today(tmp_path, 'default').read_text()
        assert 'default only line' not in _today(tmp_path, 'Processor').read_text()


@pytest.mark.asyncio
async def test_channel_rolls_to_the_next_day(app1, tmp_path):
    """A channel used by a multi-day consumer rolls over on its own."""
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        channel = log.channel('Processor')
        channel.info('day one')

        # Emit a record created tomorrow, the way a long running process would
        now = time.time()
        record = logging.LogRecord('Processor', logging.INFO, __file__, 1, 'day two', None, None)
        record.created = now + DAY
        channel.file_handler.emit(record)

        assert 'day one' in _today(tmp_path, 'Processor').read_text()
        tomorrow = tmp_path / '{}_Processor.log'.format(time.strftime('%Y-%m-%d', time.localtime(now + DAY)))
        assert 'day two' in tomorrow.read_text()
        # Nothing renamed - no .log.<date> archives anywhere
        assert not [p for p in tmp_path.iterdir() if '.log.' in p.name]


@pytest.mark.asyncio
async def test_channel_prints_to_console_by_default(app1, tmp_path):
    """A channel inherits the default console config."""
    from uvicore.logging.logger import UVICORE_LOG_THEME
    config = _config(tmp_path, {'Processor': {}})
    config['console'] = {'enabled': True, 'level': 'DEBUG', 'colors': True}

    with isolated_logger(config) as log:
        channel = log.channel('Processor')
        assert channel.console_handler is not None

        buf = io.StringIO()
        channel.console_handler._stdout = Console(theme=UVICORE_LOG_THEME, file=buf, force_terminal=False, no_color=True, width=120, markup=False, highlight=False, emoji=False)
        channel.info('on the console')
        assert 'on the console' in buf.getvalue()


@pytest.mark.asyncio
async def test_channel_console_can_be_disabled(app1, tmp_path):
    config = _config(tmp_path, {'Quiet': {'console': {'enabled': False}}})
    config['console'] = {'enabled': True, 'level': 'DEBUG', 'colors': True}

    with isolated_logger(config) as log:
        channel = log.channel('Quiet')
        assert channel.console_handler is None
        assert channel.file_handler is not None
        channel.info('file only')
        assert 'file only' in _today(tmp_path, 'Quiet').read_text()


@pytest.mark.asyncio
async def test_channel_inherits_level_and_format_but_not_filters(app1, tmp_path):
    """filters/exclude are keyed on framework logger names ('uvicore.orm'), a
    completely different naming universe than channel names - inheriting an
    include-style filter would leave every channel file silently empty."""
    config = _config(tmp_path, {'Processor': {}})
    config['file']['filters'] = ['acme']
    config['file']['exclude'] = ['Processor']

    with isolated_logger(config) as log:
        channel = log.channel('Processor')
        # Inherited
        assert channel.config.file.level == 'DEBUG'
        assert channel.config.file.format == log.config.file.format
        # NOT inherited
        assert channel.config.file.filters == []
        assert channel.config.file.exclude == []

        channel.info('not filtered out')
        assert 'not filtered out' in _today(tmp_path, 'Processor').read_text()


@pytest.mark.asyncio
async def test_channel_can_override_inherited_config(app1, tmp_path):
    channels = {'Debugger': {'file': {'level': 'WARNING', 'retention': 3}}}
    with isolated_logger(_config(tmp_path, channels)) as log:
        channel = log.channel('Debugger')
        assert channel.file_handler.level == logging.WARNING
        assert channel.file_handler.retention == 3

        channel.info('below the level')
        channel.warning('at the level')
        content = _today(tmp_path, 'Debugger').read_text()
        assert 'below the level' not in content
        assert 'at the level' in content


@pytest.mark.asyncio
async def test_unknown_channel_is_autocreated(app1, tmp_path):
    """Raising from a log call is worse than the typo it would catch."""
    with isolated_logger(_config(tmp_path)) as log:
        channel = log.channel('NeverConfigured')
        channel.info('still works')
        assert 'still works' in _today(tmp_path, 'NeverConfigured').read_text()


@pytest.mark.asyncio
async def test_channel_defined_after_bootstrap_is_honored(app1, tmp_path):
    """Logging bootstraps before package configs merge, so channel() re-reads the
    live app config rather than trusting its constructor snapshot."""
    with isolated_logger(_config(tmp_path)) as log:
        saved = uvicore.config('app.logger').get('channels')
        uvicore.config.app.logger.channels = {'LateComer': {'file': {'level': 'WARNING'}}}
        try:
            channel = log.channel('LateComer')
            assert channel.file_handler.level == logging.WARNING
        finally:
            uvicore.config.app.logger.channels = saved or {}


@pytest.mark.asyncio
async def test_channel_name_cannot_contain_a_dot(app1, tmp_path):
    """A channel named 'uvicore' would become the PARENT of 'uvicore.orm' and
    silently vacuum unrelated records into its own file."""
    with isolated_logger(_config(tmp_path)) as log:
        with pytest.raises(Exception, match='cannot contain a dot'):
            log.channel('uvicore.orm')


@pytest.mark.asyncio
async def test_channel_supports_layout_helpers_and_chaining(app1, tmp_path):
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        log.channel('Processor').nl().header('Batch 7')
        log.channel('Processor').item('500 rows')
        log.channel('Processor').item2('2 skipped', level=2)

        content = _today(tmp_path, 'Processor').read_text()
        assert ':: Batch 7 ::' in content
        assert '* 500 rows' in content
        assert '- 2 skipped' in content


@pytest.mark.asyncio
async def test_channel_levels_all_reach_the_file(app1, tmp_path):
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        channel = log.channel('Processor')
        channel.debug('a debug')
        channel.info('an info')
        channel.notice('a notice')
        channel.warning('a warning')
        channel.error('an error')
        channel.critical('a critical')

        content = _today(tmp_path, 'Processor').read_text()
        for message in ('a debug', 'an info', 'a notice', 'a warning', 'an error', 'a critical'):
            assert message in content
        assert 'NOTICE' in content, 'notice() should render its real NOTICE level'


@pytest.mark.asyncio
async def test_channel_is_safe_to_hold_across_awaits(app1, tmp_path):
    """A Channel holds no one-shot scope state, so concurrent tasks cannot
    misroute each other's lines the way a shared mutable name() scope can."""
    with isolated_logger(_config(tmp_path, {'Importer': {}, 'Auditor': {}})) as log:

        async def emit(channel_name, message):
            channel = log.channel(channel_name)
            await asyncio.sleep(0)
            channel.info(message)

        await asyncio.gather(
            emit('Importer', 'imported 500 rows'),
            emit('Auditor', 'audit complete'),
            emit('Importer', 'imported 200 more'),
        )

        importer = _today(tmp_path, 'Importer').read_text()
        auditor = _today(tmp_path, 'Auditor').read_text()
        assert 'imported 500 rows' in importer
        assert 'imported 200 more' in importer
        assert 'audit complete' not in importer
        assert 'audit complete' in auditor
        assert 'imported' not in auditor


@pytest.mark.asyncio
async def test_pending_name_scope_does_not_leak_into_a_channel(app1, tmp_path):
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        log.name('uvicore.orm')
        try:
            channel = log.channel('Processor')
            channel.info('correctly routed')
            assert channel.logger.name == 'Processor'
            assert 'correctly routed' in _today(tmp_path, 'Processor').read_text()
        finally:
            log.reset()


@pytest.mark.asyncio
async def test_channel_dump_targets_its_own_file(app1, tmp_path):
    with isolated_logger(_config(tmp_path, {'Processor': {}})) as log:
        log.channel('Processor').dump({'batch': 7})
        assert 'batch' in _today(tmp_path, 'Processor').read_text()


@pytest.mark.asyncio
async def test_channel_without_a_channel_token_still_gets_its_own_file(app1, tmp_path):
    """A path with no {channel} token must not collapse every channel into one
    shared file - that would defeat the entire point of a channel."""
    config = _config(tmp_path, {'Processor': {}, 'Auditor': {}})
    config['file']['file'] = str(tmp_path / 'app.log')

    with isolated_logger(config) as log:
        log.info('default line')
        log.channel('Processor').info('processor line')
        log.channel('Auditor').info('auditor line')

        assert (tmp_path / 'app.log').read_text().count('default line') == 1
        assert 'processor line' not in (tmp_path / 'app.log').read_text()
        assert 'processor line' in (tmp_path / 'app_Processor.log').read_text()
        assert 'auditor line' in (tmp_path / 'app_Auditor.log').read_text()


@pytest.mark.asyncio
async def test_app1_configured_channels_work_end_to_end(app1):
    """End to end against the live uvicore.log singleton and app1's REAL configured
    channels, which use a static (non dated) log path - so this also covers a
    channel riding on the legacy TimedRotatingFileHandler."""
    import os
    from uvicore.logging.handlers import DatedFileHandler

    # app1 declares these in tests/apps/app1/config/logger.py
    assert 'Processor' in uvicore.config('app.logger.channels')

    channel = uvicore.log.channel('Processor')
    assert channel.channel == 'Processor'
    assert channel.logger.propagate is False

    # app1's path is static, so the channel gets the legacy handler with the
    # channel name appended - NOT the shared /tmp/app1.log
    assert isinstance(channel.file_handler, logging.handlers.TimedRotatingFileHandler)
    assert not isinstance(channel.file_handler, DatedFileHandler)
    assert os.path.basename(channel.file_handler.baseFilename) == 'app1_Processor.log'
    assert uvicore.log.file_handler.baseFilename != channel.file_handler.baseFilename

    # The 'Quiet' channel opts out of console output
    assert uvicore.log.channel('Quiet').console_handler is None
    assert uvicore.log.channel('Auditor').console_handler is not None

    # Cached on the real singleton
    assert uvicore.log.channel('Processor') is channel
