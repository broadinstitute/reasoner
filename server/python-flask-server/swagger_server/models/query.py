# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.query_terms import QueryTerms  # noqa: F401,E501
from swagger_server import util


class Query(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, original_question: str=None, restated_question: str=None, message: str=None, terms: QueryTerms=None):  # noqa: E501
        """Query - a model defined in Swagger

        :param original_question: The original_question of this Query.  # noqa: E501
        :type original_question: str
        :param restated_question: The restated_question of this Query.  # noqa: E501
        :type restated_question: str
        :param message: The message of this Query.  # noqa: E501
        :type message: str
        :param terms: The terms of this Query.  # noqa: E501
        :type terms: QueryTerms
        """
        self.swagger_types = {
            'original_question': str,
            'restated_question': str,
            'message': str,
            'terms': QueryTerms
        }

        self.attribute_map = {
            'original_question': 'original_question',
            'restated_question': 'restated_question',
            'message': 'message',
            'terms': 'terms'
        }

        self._original_question = original_question
        self._restated_question = restated_question
        self._message = message
        self._terms = terms

    @classmethod
    def from_dict(cls, dikt) -> 'Query':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Query of this Query.  # noqa: E501
        :rtype: Query
        """
        return util.deserialize_model(dikt, cls)

    @property
    def original_question(self) -> str:
        """Gets the original_question of this Query.

        Original question as it was typed in by the user  # noqa: E501

        :return: The original_question of this Query.
        :rtype: str
        """
        return self._original_question

    @original_question.setter
    def original_question(self, original_question: str):
        """Sets the original_question of this Query.

        Original question as it was typed in by the user  # noqa: E501

        :param original_question: The original_question of this Query.
        :type original_question: str
        """

        self._original_question = original_question

    @property
    def restated_question(self) -> str:
        """Gets the restated_question of this Query.

        Restatement of the question as understood by the translator  # noqa: E501

        :return: The restated_question of this Query.
        :rtype: str
        """
        return self._restated_question

    @restated_question.setter
    def restated_question(self, restated_question: str):
        """Sets the restated_question of this Query.

        Restatement of the question as understood by the translator  # noqa: E501

        :param restated_question: The restated_question of this Query.
        :type restated_question: str
        """

        self._restated_question = restated_question

    @property
    def message(self) -> str:
        """Gets the message of this Query.

        Response from the translation engine to the user  # noqa: E501

        :return: The message of this Query.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this Query.

        Response from the translation engine to the user  # noqa: E501

        :param message: The message of this Query.
        :type message: str
        """

        self._message = message

    @property
    def terms(self) -> QueryTerms:
        """Gets the terms of this Query.


        :return: The terms of this Query.
        :rtype: QueryTerms
        """
        return self._terms

    @terms.setter
    def terms(self, terms: QueryTerms):
        """Sets the terms of this Query.


        :param terms: The terms of this Query.
        :type terms: QueryTerms
        """

        self._terms = terms
