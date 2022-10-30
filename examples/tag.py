import graphene

from graphene_federation import build_schema, key, inaccessible, shareable
from graphene_federation.tag import tag


class Product(graphene.ObjectType):
    id = graphene.ID(required=True)
    in_stock = tag(graphene.Boolean(required=True), "Products")
    out_stock = shareable(graphene.Boolean(required=True))
    adarsh = inaccessible(graphene.Boolean(required=True))


class Query(graphene.ObjectType):
    position = graphene.Field(Product)


schema = build_schema(Query, enable_federation_2=True)

query = '''
    query getSDL {
      _service {
         sdl
      }
    }
'''
result = schema.execute(query)
print(result.data)
# OrderedDict([('_service', OrderedDict([('sdl', '   extend type Message @key(fields: "id") {   id: Int! @external }  type Query {   message: Message } ')]))])
