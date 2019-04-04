# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from openapi_server.models.feedback import Feedback  # noqa: E501
from openapi_server.models.feedback_response import FeedbackResponse  # noqa: E501
from openapi_server.models.result import Result  # noqa: E501
from openapi_server.models.result_feedback import ResultFeedback  # noqa: E501
from openapi_server.test import BaseTestCase


class TestResultController(BaseTestCase):
    """ResultController integration test stubs"""

    def test_get_result(self):
        """Test case for get_result

        Request stored result
        """
        response = self.client.open(
            '/result/{result_id}'.format(result_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_result_feedback(self):
        """Test case for get_result_feedback

        Request stored feedback for this result
        """
        response = self.client.open(
            '/result/{result_id}/feedback'.format(result_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_result_feedback(self):
        """Test case for post_result_feedback

        Store feedback for a particular result
        """
        feedback = Feedback()
        response = self.client.open(
            '/result/{result_id}/feedback'.format(result_id=56),
            method='POST',
            data=json.dumps(feedback),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
