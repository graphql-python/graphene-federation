from graphql import GraphQLString

# _FieldSet = GraphQLScalarType(name="_FieldSet")

"""
To avoid _FieldSet from coming into schema we are defining it as String
"""

_FieldSet = GraphQLString
