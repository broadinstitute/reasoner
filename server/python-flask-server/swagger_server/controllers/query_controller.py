import connexion
import six

from swagger_server.models.query import Query  # noqa: E501
from swagger_server.models.response import Response  # noqa: E501
from swagger_server import util


def query(body):  # noqa: E501
    """Submit a query to the Indigo question answerer

     # noqa: E501

    :param body: Query information to be submitted
    :type body: dict | bytes

    :rtype: Response
    """
    if connexion.request.is_json:
        body = Query.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
