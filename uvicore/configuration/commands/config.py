import uvicore
import json as JSON
from uvicore.console import command, argument, option
from uvicore import app, log
from uvicore.support.dumper import dd, dump


@command()
@option('--raw', is_flag=True, help='Show output without prettyprinter')
def list(raw: bool = False):
    """List all deep merged configs from all packages"""
    if not raw:
        log.header("Final Merged Configs")
        log.line()
        dump(uvicore.config)
    else:
        print(uvicore.config)


@command()
@argument('key', default='')
@option('--raw', is_flag=True, help='Show output without prettyprinter')
def get(key: str = None, raw: bool = False):
    """Get a config value by key"""
    if not raw:
        dump(uvicore.config.dotget(key))
    else:
        print(uvicore.config.dotget(key))
