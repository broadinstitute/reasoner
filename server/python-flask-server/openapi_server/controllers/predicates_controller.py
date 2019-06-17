import connexion
import six

from openapi_server import util

from openapi_server.ui import predicates

def predicates_get():  # noqa: E501
    """summary

    description # noqa: E501


    :rtype: Dict[str, Dict[str, List[str]]]
    """
    return predicates()
