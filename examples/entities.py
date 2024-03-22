import graphene
from graphene_federation import build_schema, key


def get_file_by_id(id):
    return File(**{"id": id, "name": "test_name"})


class Author(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)


@key(fields="id")
@key(fields="id author { name }")
@key(fields="id author { id name }")
class File(graphene.ObjectType):
    id = graphene.Int(required=True)
    name = graphene.String()
    author = graphene.Field(Author, required=True)

    def resolve_id(self, info, **kwargs):
        return 1

    def resolve_name(self, info, **kwargs):
        return self.name

    def __resolve_reference(self, info, **kwargs):
        return get_file_by_id(self.id)


class Query(graphene.ObjectType):
    file = graphene.Field(File)

    def resolve_file(self, **kwargs):
        return None  # no direct access


schema = build_schema(Query)

query = """
    query getSDL {
      _service {
         sdl
      }
    }
"""
result = schema.execute(query)
print(result.data)
# {'_service': {'sdl': 'type Query {\n  file: File\n}\n\ntype File @key(fields: "id") {\n  id: Int!\n  name: String\n}'}}

query = """
    query entities($_representations: [_Any!]!) {
      _entities(representations: $_representations) {
        ... on File {
          id
          name
        }
      }
    }
    
"""

result = schema.execute(
    query, variables={"_representations": [{"__typename": "File", "id": 1}]}
)
print(result.data)
# {'_entities': [{'id': 1, 'name': 'test_name'}]}
