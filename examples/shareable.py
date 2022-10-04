import graphene
from graphene_federation.shareable import shareable

from graphene_federation import build_schema


@shareable
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = shareable(graphene.Int(required=True))


class Query(graphene.ObjectType):
    position = graphene.Field(Position)


schema = build_schema(Query)

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
