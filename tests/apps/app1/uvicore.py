#!/usr/bin/env python

import uvicore
from app1.services import bootstrap


# Bootstrap the Uvicore application
app = bootstrap.application(is_console=True)

# Initialize CLI
if __name__ == '__main__':
    # Run the main click group by executing the actual method in the Ioc
    cli = uvicore.ioc.make('Console')
    cli(_anyio_backend='asyncio')
