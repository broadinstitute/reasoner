# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from openapi_server.test import BaseTestCase


class TestPredicatesController(BaseTestCase):
    """PredicatesController integration test stubs"""

    def test_predicates_get(self):
        """Test case for predicates_get

        summary
        """
        response = self.client.open(
            '/reasoner/api/v1/predicates',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
