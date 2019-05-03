import connexion
import six

from openapi_server.models.message import Message  # noqa: E501
from openapi_server.models.query import Query
from openapi_server import util

from openapi_server.ui import queryReasoner
from openapi_server.ui import queryGraph2query


def query(request_body):  # noqa: E501
    """Query reasoner via one of several inputs

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: dict | bytes

    :rtype: Message
    """
    if connexion.request.is_json:
        body = Query.from_dict(connexion.request.get_json())  # noqa: E501

        if body.query_message != None:
            query_type_id = body.query_message.query_type_id
            terms = body.query_message.terms

            if body.query_message.query_graph != None:
                return queryGraph2query(body.query_message.query_graph)

            if query_type_id != None:
                return queryReasoner(query_type_id, terms)

            return( { "status": 400, "title": "query_graph or query_type_id not defined", "detail": "query_graph or query_type_id not defined", "type": "about:blank" }, 400 )
        return( { "status": 400, "title": "query_message not defined", "detail": "query_message not defined", "type": "about:blank" }, 400 )
    return( { "status": 400, "title": "body content not JSON", "detail": "Required body content is not JSON", "type": "about:blank" }, 400 )

