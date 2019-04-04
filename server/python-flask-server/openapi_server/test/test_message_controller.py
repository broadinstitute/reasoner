# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from openapi_server.models.message import Message  # noqa: E501
from openapi_server.models.message_feedback import MessageFeedback  # noqa: E501
from openapi_server.test import BaseTestCase


class TestMessageController(BaseTestCase):
    """MessageController integration test stubs"""

    def test_get_message(self):
        """Test case for get_message

        Request stored messages and results from reasoner
        """
        response = self.client.open(
            '/message/{message_id}'.format(message_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_message_feedback(self):
        """Test case for get_message_feedback

        Request stored feedback for this message from reasoner
        """
        response = self.client.open(
            '/message/{message_id}/feedback'.format(message_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
