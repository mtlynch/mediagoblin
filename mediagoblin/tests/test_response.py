# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

from werkzeug.wrappers import Request

from ..tools.response import redirect, redirect_obj

class TestRedirect(object):
    def test_redirect_respects_location(self):
        """Test that redirect returns a 302 to location specified."""
        request = Request({})
        response = redirect(request, location='/test')
        assert response.status_code == 302
        assert response.location == '/test'

    def test_redirect_respects_querystring(self):
        """Test that redirect includes querystring in returned location."""
        request = Request({})
        response = redirect(request, location='', querystring='#baz')
        assert response.location == '#baz'

    def test_redirect_respects_urlgen_args(self):
        """Test that redirect returns a 302 to location from urlgen args."""

        # Using a mock urlgen here so we're only testing redirect itself. We
        # could instantiate a url_map and map_adaptor with WSGI environ as per
        # app.py, but that would really just be testing Werkzeug.
        def urlgen(endpoint, **kwargs):
            return '/test?foo=bar'

        request = Request({})
        request.urlgen = urlgen
        response = redirect(request, 'test-endpoint', foo='bar')
        assert response.status_code == 302
        assert response.location == '/test?foo=bar'

    def test_redirect_obj_calls_url_for_self(self):
        """Test that redirect_obj returns a 302 to obj's url_for_self()."""

        # Using a mock obj here so that we're only testing redirect_obj itself,
        # rather than also testing the url_for_self implementation.
        class Foo(object):
            def url_for_self(*args, **kwargs):
                return '/foo'

        request = Request({})
        request.urlgen = None
        response = redirect_obj(request, Foo())
        assert response.status_code == 302
        assert response.location == '/foo'
