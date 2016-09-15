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

try:
    import mock
except ImportError:
    import unittest.mock as mock

from werkzeug.wrappers import Request
from werkzeug.test import EnvironBuilder

from mediagoblin.tools.request import decode_request
from mediagoblin.tools.pagination import Pagination

class TestDecodeRequest(object):
    """Test the decode_request function."""

    def test_form_type(self):
        """Try a normal form-urlencoded request."""
        builder = EnvironBuilder(method='POST', data={'foo': 'bar'})
        request = Request(builder.get_environ())
        data = decode_request(request)
        assert data['foo'] == 'bar'

    def test_json_type(self):
        """Try a normal JSON request."""
        builder = EnvironBuilder(
            method='POST', content_type='application/json',
            data='{"foo": "bar"}')
        request = Request(builder.get_environ())
        data = decode_request(request)
        assert data['foo'] == 'bar'

    def test_content_type_with_options(self):
        """Content-Type can also have options."""
        builder = EnvironBuilder(
            method='POST',
            content_type='application/x-www-form-urlencoded; charset=utf-8')
        request = Request(builder.get_environ())
        # Must populate form field manually with non-default content-type.
        request.form = {'foo': 'bar'}
        data = decode_request(request)
        assert data['foo'] == 'bar'

    def test_form_type_is_default(self):
        """Assume form-urlencoded if blank in the request."""
        builder = EnvironBuilder(method='POST', content_type='')
        request = Request(builder.get_environ())
        # Must populate form field manually with non-default content-type.
        request.form = {'foo': 'bar'}
        data = decode_request(request)
        assert data['foo'] == 'bar'


class TestPagination(object):
    def _create_paginator(self, num_items, page, per_page):
        """Create a Paginator with a mock database cursor."""
        mock_cursor = mock.MagicMock()
        mock_cursor.count.return_value = num_items
        return Pagination(page, mock_cursor, per_page)

    def test_creates_valid_page_url_from_explicit_base_url(self):
        """Check that test_page_url_explicit runs.

        This is a regression test for a Python 2/3 compatibility fix.

        """
        paginator = self._create_paginator(num_items=1, page=1, per_page=30)
        url = paginator.get_page_url_explicit('http://example.com', [], 1)
        assert url == 'http://example.com?page=1'

    def test_iter_pages_handles_single_page(self):
        """Check that iter_pages produces the expected result for single page.

        This is a regression test for a Python 2/3 compatibility fix.

        """
        paginator = self._create_paginator(num_items=1, page=1, per_page=30)
        assert list(paginator.iter_pages()) == [1]

    def test_zero_items(self):
        """Check that no items produces no pages."""
        paginator = self._create_paginator(num_items=0, page=1, per_page=30)
        assert paginator.total_count == 0
        assert paginator.pages == 0

    def test_single_item(self):
        """Check that one item produces one page."""
        paginator = self._create_paginator(num_items=1, page=1, per_page=30)
        assert paginator.total_count == 1
        assert paginator.pages == 1

    def test_full_page(self):
        """Check that a full page of items produces one page."""
        paginator = self._create_paginator(num_items=30, page=1, per_page=30)
        assert paginator.total_count == 30
        assert paginator.pages == 1

    def test_multiple_pages(self):
        """Check that more than a full page produces two pages."""
        paginator = self._create_paginator(num_items=31, page=1, per_page=30)
        assert paginator.total_count == 31
        assert paginator.pages == 2
