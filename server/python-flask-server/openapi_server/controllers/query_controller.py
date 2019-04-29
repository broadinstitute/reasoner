import connexion
import six

from openapi_server.models.message import Message  # noqa: E501
from openapi_server.models.query import Query
from openapi_server import util

from openapi_server.ui import *


def query(request_body):  # noqa: E501
    """Query reasoner via one of several inputs

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: dict | bytes

    :rtype: Message
    """
    if connexion.request.is_json:
        body = Query.from_dict(connexion.request.get_json())  # noqa: E501
        query_type_id = body.query_message.query_type_id
        terms = body.query_message.terms

        r = 'wrong query_message.query_type_id \''+query_type_id+'\''
        if query_type_id == 'Q2':
            r = cop_query(terms.chemical_substance, terms.disease)
        elif query_type_id == 'Q3':
            r = mvp_target_query(terms.chemical_substance)
        elif query_type_id == 'conditionToSymptoms':
            r = conditionToSymptoms(terms.disease)
        elif query_type_id == 'symptomToConditions':
            r = symptomToConditions(terms.symptom)
        elif query_type_id == 'conditionSymptomSimilarity':
            r = conditionSymptomSimilarity(terms.disease)
        elif query_type_id == 'genesToPathways':
            r = genesToPathways(terms.genes)
        elif query_type_id == 'pathwayToGenes':
            r = pathwayToGenes(terms.pathway)
        elif query_type_id == 'geneToCompound':
            r = geneToCompound(terms.gene)
        elif query_type_id == 'compoundToIndication':
            r = compoundToIndication(terms.chemical_substance)
        elif query_type_id == 'compoundToPharmClass':
            r = compoundToPharmClass(terms.chemical_substance)

        return r

    return 'wrong request format'
