import uvicore
from typing import Dict, Any
from uvicore.support.provider import ServiceProvider
from uvicore.support.dumper import dump, dd


class Http(ServiceProvider):

    def register(self) -> None:
        """Register package into uvicore framework.
        All packages are registered before the framework boots.  This is where
        you define your packages configs and IoC bindings.  Configs are deep merged only after
        all packages are registered.  No real work should be performed here as it
        is very early in the bootstraping process and most internal processes are not
        instantiated yet.
        """

        # Register IoC bindings only if running in HTTP mode
        if self.app.is_http:
            override = self.binding('Http')
            self.bind(
                name='Http',
                object=override or 'uvicore.http.server._Server',
                singleton=True,
                kwargs={
                    'debug': uvicore.config('app.debug'),
                    'title': uvicore.config('app.openapi.title'),
                    'version': uvicore.app.version,
                    'openapi_url': uvicore.config('app.openapi.url'),
                    'docs_url': uvicore.config('app.openapi.docs_url'),
                    'redoc_url': uvicore.config('app.openapi.redoc_url'),
                },
                aliases=['http', 'HTTP']
            )

            # Set app.http instance variable
            self.app._http = uvicore.ioc.make('Http')
            self.app._is_async = True

            # Register event listeners as methods
            #self.listen('uvicore.foundation.events.app.Registered', self.registered)
            self.events.listen('uvicore.foundation.events.app.Booted', self.booted)

            # Register as a listener class
            #self.listen('uvicore.foundation.events.app.Booted', 'uvicore.http.listeners.mount_static_assets.MountStaticAssets')

            # Register a subscriber class
            #self.subscribe('uvicore.http.listeners.subscription.HttpEventSubscription')

            # # Multi event listener
            # self.listen([
            #     'uvicore.foundation.events.app.Booted',
            #     'uvicore.foundation.events.app.Registered',
            # ], self.multi)

            # Wilecard event listener
            #self.listen('uvicore.foundation.events.*', self.multi)


    def boot(self) -> None:
        """Bootstrap package into uvicore framework.
        Boot takes place after all packages are registered.  This means all package
        configs are deep merged to provide a complete and accurate view of all configs.
        This is where you load views, assets, routes, commands...
        """
        pass

    def registered(self, event: str, payload: Any) -> None:
        pass
        #dump("registered event handler")
        #dd(event, payload, payload.__dict__)


    def booted(self, event: str, payload: Any) -> None:
        """Custom event handler for uvicore.foundation.events.booted"""
        #dd(event, payload.__dict__)
        self.mount_static_assets()
        self.create_template_environment()

    def multi(self, event: str, payload: Any) -> None:
        dump(event, payload.__dict__)
        if event['name'] == 'uvicore.foundation.events.app.Booted':
            dd('done')

    def mount_static_assets(self) -> None:
        """Mount /static route using all packages static paths"""
        from uvicore.http.static import StaticFiles

        # Get all packages asset paths
        paths = []
        for package in self.app.packages.values():
            for path in package.asset_paths:
                if path not in paths:
                    paths.append(path)

        # Mount all directories to /assets
        # Last directory defined WINS, which fits our last provider wins
        self.app.http.mount('/static', StaticFiles(directories=paths), name='static')

    def create_template_environment(self) -> None:
        """Create template environment with settings from all packages"""
        from uvicore.http import templates

        # Instantiate template system
        self.app._template = templates.Jinja()

        # Add all package view paths to template environment
        for package in self.app.packages.values():
            for path in package.view_paths:
                self.app.template.include_path(path)

            # Add all package template options to template environment
            options = package.template_options
            if 'context_functions' in options:
                for f in options['context_functions']:
                    self.app.template.include_context_function(**f)
            if 'context_filters' in options:
                for f in options['context_filters']:
                    self.app.template.include_context_filter(**f)
            if 'filters' in options:
                for f in options['filters']:
                    self.app.template.include_filter(**f)
            if 'tests' in options:
                for f in options['tests']:
                    self.app.template.include_test(**f)

        # Create new template environment
        self.app.template.init()
