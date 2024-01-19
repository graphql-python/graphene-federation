import graphene

from graphene_federation import (
    LATEST_VERSION, build_schema,
    shareable,
    external,
    key,
    override,
    inaccessible,
)


@key(fields="id")
class Product(graphene.ObjectType):
    id = graphene.ID(required=True)
    in_stock = override(graphene.Boolean(required=True), "Products")
    out_stock = inaccessible(graphene.Boolean(required=True))


class Query(graphene.ObjectType):
    position = graphene.Field(Product)


schema = build_schema(Query, federation_version=LATEST_VERSION)

query = """
    query getSDL {
      _service {
         sdl
      }
    }
"""
result = schema.execute(query)
print(result.data)
# {'_service': {'sdl': 'extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@key", "@override", "@inaccessible"])\ntype Query {\n  position: Product\n}\n\ntype Product @key(fields: "id") {\n  id: ID!\n  inStock: Boolean! @override(from: "Products")\n  outStock: Boolean! @inaccessible\n}'}}
