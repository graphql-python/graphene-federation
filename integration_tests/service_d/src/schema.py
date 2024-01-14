from graphene import Field, Int, ObjectType

from graphene_federation import build_schema, extends, external, key

"""
Alphabet order - matters
Y should be just after X in sdl
https://github.com/preply/graphene-federation/issues/26#issuecomment-572127271
"""


@key(fields="id")
@extends
class Article(ObjectType):
    id = external(Int(required=True))


class X(ObjectType):
    x_article = Field(Article)


class Y(ObjectType):
    id = Int(required=True)


class Query(ObjectType):
    x = Field(X)
    y = Field(Y)


schema = build_schema(query=Query)
