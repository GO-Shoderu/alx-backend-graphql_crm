import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

# Project-level Query that extends the CRM app Query
class Query(CRMQuery, graphene.ObjectType):
    pass

# Project-level Mutation that extends the CRM app Mutation
class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
