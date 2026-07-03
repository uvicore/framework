"""
Tests for HTTP view composers.

Covers the @uvicore.composer() decorator binding, provider registration via
register_http_view_composers() (including the dict form, which the app1 provider
uses on every boot), the aggregation of each package's composers into
uvicore.config.uvicore.http.view_composers, and the end-to-end merge that
happens inside response.View() when a rendered view matches a composer wildcard.
"""
import pytest
import uvicore


@pytest.mark.asyncio
async def test_dict_form_registration(app1):
    """The app1 provider registers composers via the dict form.

    This is the regression guard for the dict-form branch of
    register_http_view_composers() (it previously called a non-existent
    self.composers() helper and raised AttributeError during boot).  The
    per-package registration runs during provider boot() regardless of HTTP mode.
    """
    composers = uvicore.app.package('app1').web.view_composers

    # Layout was registered with a single 'app1/*' wildcard string (normalized to a list)
    assert composers['app1.http.composers.layout.Layout'] == ['app1/*']

    # Sidebar was registered with an explicit list of views
    assert composers['app1.http.composers.sidebar.Sidebar'] == ['app1/home', 'app1/about']


@pytest.mark.asyncio
async def test_composer_bound_in_ioc(app1):
    """The @uvicore.composer() decorator binds the class into the IoC container."""
    composer = uvicore.ioc.make('app1.http.composers.layout.Layout')
    assert composer is not None
    assert composer.__name__ == 'Layout'


@pytest.mark.asyncio
async def test_composers_aggregated_into_config(webserver):
    """Each package's composers are merged into uvicore.config.uvicore.http.view_composers."""
    composers = uvicore.config.uvicore.http.view_composers
    assert composers['app1.http.composers.layout.Layout'] == ['app1/*']
    assert composers['app1.http.composers.sidebar.Sidebar'] == ['app1/home', 'app1/about']


@pytest.mark.asyncio
async def test_composer_runs_and_merges_into_view_context(webserver):
    """Rendering a view that matches a composer wildcard injects the composed context."""
    from uvicore.http import response

    # 'app1/composed' matches the Layout composer's 'app1/*' wildcard, so the
    # composer's returned dict is merged into the context before rendering.
    result = await response.View('app1/composed.j2', {'request': None})
    assert b'composed_marker=app1-layout' in result.body


@pytest.mark.asyncio
async def test_controller_context_wins_over_composer(webserver):
    """A key set by the controller is NOT overwritten by the composer (defaults merge)."""
    from uvicore.http import response

    result = await response.View('app1/composed.j2', {
        'request': None,
        'composed_marker': 'controller-wins',
    })
    assert b'composed_marker=controller-wins' in result.body
