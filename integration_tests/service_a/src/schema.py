from graphene import Field, Int, Interface, List, NonNull, ObjectType, String

from graphene_federation import FederationVersion, build_schema, extends, external, key


class DecoratedText(Interface):
    color = Int(required=True)


@key(fields="id")
@extends
class FileNode(ObjectType):
    id = external(Int(required=True))


@key(fields="id")
@extends
class FunnyText(ObjectType):
    class Meta:
        interfaces = (DecoratedText,)

    id = external(Int(required=True))

    def resolve_color(self, info, **kwargs):
        return self.id + 2


class FunnyTextAnother(ObjectType):
    """
    To test @extend on types with same prefix
    """

    class Meta:
        interfaces = (DecoratedText,)

    id = Int(required=True)

    def resolve_color(self, info, **kwargs):
        return self.id + 2


@key(fields="primaryEmail")
@extends
class User(ObjectType):
    primaryEmail = external(String())


class Post(ObjectType):
    id = Int(required=True)
    title = String(required=True)
    text = Field(lambda: FunnyText)
    files = List(NonNull(FileNode))
    author = Field(lambda: User)


class Query(ObjectType):
    goodbye = String()
    posts = List(NonNull(Post))

    def resolve_posts(root, info):
        return [
            Post(id=1, title="title1", text=FunnyText(id=1), files=[FileNode(id=1)]),
            Post(
                id=2,
                title="title2",
                text=FunnyText(id=2),
                files=[FileNode(id=2), FileNode(id=3)],
            ),
            Post(id=3, title="title3", text=FunnyText(id=3)),
            Post(
                id=4,
                title="title4",
                text=FunnyText(id=4),
                author=User(primaryEmail="frank@frank.com"),
            ),
        ]

    def resolve_goodbye(root, info):
        return "See ya!"


schema = build_schema(
    query=Query,
    types=[FunnyTextAnother],
    federation_version=FederationVersion.VERSION_1_0,
    auto_camelcase=False,
)
