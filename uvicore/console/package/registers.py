from uvicore.typing import Dict


class Cli:
    """CLI Service Provider Mixin"""

    def register_cli_commands(self, items: Dict[str, Dict] = None, *, group: str = None, help: str = None, commands: Dict = None):
        """Add commands as a dictionary or kwargs"""

        # Default registration
        self.package.registers.defaults({'commands': True})

        # Register commands only if allowed
        if not self.package.registers.commands: return

        if items:
            # Add as dictionary
            self.package.console.groups.merge(items)
        else:
            # Add as kwargs
            if help:
                self.package.console.groups.merge({
                    group: {
                        'help': help,
                        'commands': commands
                    }
                })
            else:
                self.package.console.groups.merge({
                    group: {
                        'commands': commands
                    }
                })
