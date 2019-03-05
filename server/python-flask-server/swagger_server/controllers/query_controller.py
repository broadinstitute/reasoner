import connexion
import six

from swagger_server.models.query import Query  # noqa: E501
from swagger_server.ui import *


def query(body):  # noqa: E501
    """Submit a query to the Indigo question answerer

     # noqa: E501

    :param body: Query information to be submitted
    :type body: dict | bytes

    :rtype: Response
    """
    if connexion.request.is_json:
        body = Query.from_dict(connexion.request.get_json())  # noqa: E501

        if body.query_type_id == 'Q2':
            r = cop_query(body.terms.chemical_substance, body.terms.disease)
        elif body.query_type_id == 'Q3':
            r = mvp_target_query(body.terms.chemical_substance)
        elif body.query_type_id == 'conditionToSymptoms':
            r = conditionToSymptoms(body.terms.disease)
        elif body.query_type_id == 'symptomToConditions':
            r = symptomToConditions(body.terms.symptom)
        elif body.query_type_id == 'genesToPathways':
            r = genesToPathways(body.terms.genes)
        elif body.query_type_id == 'pathwayToGenes':
            r = pathwayToGenes(body.terms.pathway)
        elif body.query_type_id == 'geneToCompound':
            r = geneToCompound(body.terms.gene)
        elif body.query_type_id == 'compoundToIndication':
            r = compoundToIndication(body.terms.chemical_substance)
        elif body.query_type_id == 'compoundToPharmClass':
            r = compoundToPharmClass(body.terms.chemical_substance)

    return(r)
