import graphene

from graphene_federation import build_schema, shareable, external, key, override, inaccessible


@key(fields="id")
class Product(graphene.ObjectType):
    id = graphene.ID(required=True)
    in_stock = override(graphene.Boolean(required=True), "Products")
    out_stock = inaccessible(graphene.Boolean(required=True))


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
