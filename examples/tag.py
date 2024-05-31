import graphene
from graphene_federation.tag import tag

from graphene_federation import LATEST_VERSION, build_schema, inaccessible, shareable


class Product(graphene.ObjectType):
    id = graphene.ID(required=True)
    in_stock = tag(graphene.Boolean(required=True), "Products")
    out_stock = shareable(graphene.Boolean(required=True))
    is_listed = inaccessible(graphene.Boolean(required=True))


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
# {'_service': {'sdl': 'extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@inaccessible", "@shareable", "@tag"])\ntype Query {\n  position: Product\n}\n\ntype Product  {\n  id: ID!\n  inStock: Boolean! @tag(name: "Products")\n  outStock: Boolean! @shareable\n  isListed: Boolean! @inaccessible\n}'}}
