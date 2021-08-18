import uvicore
from uvicore.support.dumper import dump, dd
from uvicore.exceptions import SmartException
from uvicore.console import command, argument, option


# ------------------------------------------------------------------------------
# Uvicore Command Schematic
# This schematic is filled with examples, a suppliment to the docs.
# Pick the best example for your use case and modify as needed!
# ------------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Example: Basic command with on arguments or options
# --------------------------------------------------------------------------
@command()
async def cli():
    """xx_AppName xx_name CLI command"""
    try:
        print('Welcome to your new xx_AppName xx_name CLI command!')
    except SmartException as e:
        # Python exit() with any value means "error" in bash exit code speak!
        exit(e.detail)




# --------------------------------------------------------------------------
# Example: Command with arguments and options
# --------------------------------------------------------------------------
# @command(help="This is another place to set command help messages")
# @argument('id_or_name')
# @option('--tenant', help='Tenant')
# @option('--coin', default='BTC', help='Coin with Default')
# @option('--json', is_flag=True, help='Output results as JSON')
# async def get(id_or_name: str, tenant: str, coin: str, json: bool):
#     """This shows up as the commands help message"""
#     # ex: ./uvicore xx_name namearg --tenant bob --json
#     from uvicore.exceptions import SmartException
#     try:
#         # Do stuff
#         pass
#     except SmartException as e:
#         # Python exit() with any value means "error" in bash exit code speak!
#         exit(e.detail)
