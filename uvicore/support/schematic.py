import os
import shutil
import uvicore
import fileinput
from uvicore import log
from typing import List
from uvicore.support import str
from uvicore.support.dumper import dump, dd


class Schematic:

    def __init__(self, *, type: str, stub: str, dest: str, replace: List):
        self.type = type
        self.package = uvicore.app.package(main=True)
        self.stub = os.path.realpath(stub)
        self.dest = os.path.realpath(dest)
        self.path = "/".join(self.dest.split('/')[0:-1])

        # Replacements (order is important)
        self.replacements = replace
        self.replacements.extend([
            ("xx_vendor", self.package.vendor),
            ("xx_Vendor", str.studly(self.package.vendor)),
            ("xx_appname", self.package.short_name),
            ("xx_AppName", str.studly(self.package.short_name)),
        ])

    def generate(self):
        log.header('Generating new schematic')
        log.item2('Type: ' + self.type)
        log.item2('Stub: ' + self.stub)
        log.item2('Destination: ' + self.dest)
        log.item2('Replacements:')
        log.dump(self.replacements)

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        if os.path.exists(self.dest):
            #raise Exception('Destination file already exists')
            log.nl(); log.error('ERROR: Destination file already exists.  Schematic cancelled.')
            exit()

        # Copy stub
        log.item4('Copying stub to destination')
        shutil.copyfile(self.stub, self.dest)

        # Search and Replace
        log.item4('Searching and replacing keywords in destination stub')
        with fileinput.FileInput(self.dest, inplace=True) as f:
            for line in f:
                for replacement in self.replacements:
                    line = line.replace(replacement[0], replacement[1])
                print(line, end="")


