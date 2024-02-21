import uvicore
from uvicore.typing import Dict, List, OrderedDict, get_type_hints, Tuple
from uvicore.events import Handler
from uvicore.support import module
from uvicore.support.dumper import dump, dd
from uvicore.foundation.events.app import Booted as OnAppBooted
from uvicore.contracts import Package as Package
from uvicore.console import command_is
from starlette.applications import Starlette
from fastapi import FastAPI, Depends
from uvicore.http import response
from uvicore.http.events import server as HttpServerEvents
from uvicore.http.routing.router import Routes
from functools import partial, update_wrapper
from uvicore.http.routing import ApiRoute, WebRoute
from uvicore.http.routing import Guard
from uvicore.http.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html


class Templating(Handler):

    def __call__(self, event: OnAppBooted):
        """Bootstrap the Templating System after the Application is Booted"""

        # Initialize Templating System
        self.initialize_templates()


    def initialize_templates(self) -> None:
        """Initialize Templating System"""

        # Loop each package with an HTTP definition and add to our HTTP server
        paths = []
        context_processors = Dict()
        for package in uvicore.app.packages.values():
            if not 'templating' in package: continue

            # Append template paths
            for path in package.templating.paths or []:
                paths.append(path)

            # Deep merge template context_processors
            context_processors.merge(package.templating.context_processors or {})

        # Get the template singleton from the IoC
        templates = uvicore.ioc.make('uvicore.templating.engine.Templates')

        # Add all packages view paths
        # First path wins, so we must REVERSE the package order
        # This will set the main running app FIRST as we always want the app to win
        paths.reverse()
        for path in paths:
            templates.include_path(module.location(path))

        # Add all packages deep_merged template options
        if 'context_functions' in context_processors:
            for name, method in context_processors['context_functions'].items():
                templates.include_context_function(name, method)
        if 'context_filters' in context_processors:
            for name, method in context_processors['context_filters'].items():
                templates.include_context_filter(name, method)
        if 'filters' in context_processors:
            for name, method in context_processors['filters'].items():
                templates.include_filter(name, method)
        if 'tests' in context_processors:
            for name, method in context_processors['tests'].items():
                templates.include_test(name, method)

        # Initialize template system
        templates._init()
