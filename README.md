# graphene-federation

Federation support for ![Graphene Logo](http://graphene-python.org/favicon.png) [Graphene](http://graphene-python.org) following the [Apollo Federation specifications](https://www.apollographql.com/docs/federation/subgraph-spec).

[![PyPI version][pypi-image]][pypi-url]
[![Unit Tests Status][unit-tests-image]][unit-tests-url]
[![Coverage Status][coveralls-image]][coveralls-url]
[![Integration Tests Status][integration-tests-image]][integration-tests-url]

[pypi-image]: https://badge.fury.io/py/graphene-federation.svg
[pypi-url]: https://pypi.org/project/graphene-federation/
[unit-tests-image]: https://github.com/graphql-python/graphene-federation/workflows/Unit%20Tests/badge.svg?branch=main
[unit-tests-url]: https://github.com/graphql-python/graphene-federation/actions?query=workflow%3A"Unit+Tests"
[coveralls-image]: https://coveralls.io/repos/github/graphql-python/graphene-federation/badge.svg?branch=main
[coveralls-url]: https://coveralls.io/github/graphql-python/graphene-federation?branch=main
[integration-tests-image]: https://github.com/graphql-python/graphene-federation/workflows/Integration%20Tests/badge.svg?branch=main
[integration-tests-url]: https://github.com/graphql-python/graphene-federation/actions?query=workflow%3A"Integration+Tests"


This repository is heavily based on the repo it was forked from... Huge thanks to [Preply for setting up the foundations](https://medium.com/preply-engineering/apollo-federation-support-in-graphene-761a0512456d).


WARNING: This version is not compatible with `graphene` version below v3.
If you need to use a version compatible with `graphene` v2 I recommend using the version 1.0.0 of `graphene_federation`.

------------------------

## Supported Features

* `sdl` (`_service` on field): enable to add schema in federation (as is)

## Apollo Spec Supported

- [x] v1.0
- [x] v2.0
- [x] v2.1
- [x] v2.2
- [x] v2.3
- [x] v2.4
- [x] v2.5 
- [x] v2.6 `STABLE_VERSION` . Rover dev supports only upto v2.6
- [x] v2.7 `LATEST_VERSION`

All directives could be easily integrated with the help of [graphene-directives](https://github.com/strollby/graphene-directives). 
Now every directive's values are validated at run time itself by [graphene-directives](https://github.com/strollby/graphene-directives).

### Directives (v2.7)

```graphql
directive @composeDirective(name: String!) repeatable on SCHEMA
directive @extends on OBJECT | INTERFACE
directive @external on OBJECT | FIELD_DEFINITION
directive @key(fields: FieldSet!, resolvable: Boolean = true) repeatable on OBJECT | INTERFACE
directive @inaccessible on
  | FIELD_DEFINITION
  | OBJECT
  | INTERFACE
  | UNION
  | ENUM
  | ENUM_VALUE
  | SCALAR
  | INPUT_OBJECT
  | INPUT_FIELD_DEFINITION
  | ARGUMENT_DEFINITION
directive @interfaceObject on OBJECT
directive @override(from: String!, label: String) on FIELD_DEFINITION
directive @provides(fields: FieldSet!) on FIELD_DEFINITION
directive @requires(fields: FieldSet!) on FIELD_DEFINITION
directive @shareable repeatable on FIELD_DEFINITION | OBJECT
directive @tag(name: String!) repeatable on
  | FIELD_DEFINITION
  | INTERFACE
  | OBJECT
  | UNION
  | ARGUMENT_DEFINITION
  | SCALAR
  | ENUM
  | ENUM_VALUE
  | INPUT_OBJECT
  | INPUT_FIELD_DEFINITION
directive @authenticated on
    FIELD_DEFINITION
  | OBJECT
  | INTERFACE
  | SCALAR
  | ENUM
directive @requiresScopes(scopes: [[federation__Scope!]!]!) on
    FIELD_DEFINITION
  | OBJECT
  | INTERFACE
  | SCALAR
  | ENUM
directive @policy(policies: [[federation__Policy!]!]!) on
  | FIELD_DEFINITION
  | OBJECT
  | INTERFACE
  | SCALAR
  | ENUM
scalar federation__Policy
scalar federation__Scope
scalar FieldSet
```

Read about directives in [official documentation](https://www.apollographql.com/docs/federation/federated-types/federated-directives)


Each type which is decorated with `@key` or `@extends` is added to the `_Entity` union.
The [`__resolve_reference` method](https://www.apollographql.com/docs/federation/api/apollo-federation/#__resolvereference) can be defined for each type that is an entity.
Note that since the notation with double underscores can be problematic in Python for model inheritance this resolver method can also be named `_resolve_reference` (the `__resolve_reference` method will take precedence if both are declared).

This method is called whenever an entity is requested as part of the fulfilling a query plan.
If not explicitly defined, the default resolver is used.
The default resolver just creates instance of type with passed fieldset as kwargs, see [`entity.get_entity_query`](graphene_federation/entity.py) for more details
* You should define `__resolve_reference`, if you need to extract object before passing it to fields resolvers (example: [FileNode](integration_tests/service_b/src/schema.py))
* You should not define `__resolve_reference`, if fields resolvers need only data passed in fieldset (example: [FunnyText](integration_tests/service_a/src/schema.py))
Read more in [official documentation](https://www.apollographql.com/docs/apollo-server/api/apollo-federation/#__resolvereference).

------------------------

## Example

Here is an example of implementation based on the [Apollo Federation introduction example](https://www.apollographql.com/docs/federation/).
It implements a federation schema for a basic e-commerce application over three services: accounts, products, reviews.

### Accounts
First add an account service that expose a `User` type that can then be referenced in other services by its `id` field:

```python
from graphene import Field, Int, ObjectType, String

from graphene_federation import LATEST_VERSION, build_schema, key


@key("id")
class User(ObjectType):
    id = Int(required=True)
    username = String(required=True)

    def __resolve_reference(self, info, **kwargs):
        """
        Here we resolve the reference of the user entity referenced by its `id` field.
        """
        return User(id=self.id, email=f"user_{self.id}@mail.com")


class Query(ObjectType):
    me = Field(User)


schema = build_schema(query=Query, federation_version=LATEST_VERSION)
```

### Product
The product service exposes a `Product` type that can be used by other services via the `upc` field:

```python
from graphene import Argument, Int, List, ObjectType, String

from graphene_federation import LATEST_VERSION, build_schema, key


@key("upc")
class Product(ObjectType):
    upc = String(required=True)
    name = String(required=True)
    price = Int()

    def __resolve_reference(self, info, **kwargs):
        """
        Here we resolve the reference of the product entity referenced by its `upc` field.
        """
        return Product(upc=self.upc, name=f"product {self.upc}")


class Query(ObjectType):
    topProducts = List(Product, first=Argument(Int, default_value=5))


schema = build_schema(query=Query, federation_version=LATEST_VERSION)
```

### Reviews
The reviews service exposes a `Review` type which has a link to both the `User` and `Product` types.
It also has the ability to provide the username of the `User`.
On top of that it adds to the `User`/`Product` types (that are both defined in other services) the ability to get their reviews.

```python
from graphene import Field, Int, List, ObjectType, String

from graphene_federation import LATEST_VERSION, build_schema, external, key, provides


@key("id")
class User(ObjectType):
    id = external(Int(required=True))
    reviews = List(lambda: Review)

    def resolve_reviews(self, info, *args, **kwargs):
        """
        Get all the reviews of a given user. (not implemented here)
        """
        return []


@key("upc")
class Product(ObjectType):
    upc = external(String(required=True))
    reviews = List(lambda: Review)


class Review(ObjectType):
    body = String()
    author = provides(Field(User), fields="username")
    product = Field(Product)


class Query(ObjectType):
    review = Field(Review)


schema = build_schema(query=Query, federation_version=LATEST_VERSION)
```

### Federation

Note that each schema declaration for the services is a valid graphql schema (it only adds the `_Entity` and `_Service` types).
The best way to check that the decorator are set correctly is to request the service sdl:

```python
from graphql import graphql

query = """
query {
    _service {
        sdl
    }
}
"""

result = graphql(schema, query)
print(result.data["_service"]["sdl"])
```

Those can then be used in a federated schema.

You can find more examples in the unit / integration tests and [examples folder](examples/).

There is also a cool [example](https://github.com/preply/graphene-federation/issues/1) of integration with Mongoengine.

------------------------
## Other Notes

### build_schema new arguments

- `schema_directives` (`Collection[SchemaDirective]`): Directives that can be defined at `DIRECTIVE_LOCATION.SCHEMA` with their argument values.
- `include_graphql_spec_directives` (`bool`): Includes directives defined by GraphQL spec (`@include`, `@skip`, `@deprecated`, `@specifiedBy`)
- `federation_version` (`FederationVersion`): Specify the version explicit (default STABLE_VERSION)

### Directives Additional arguments

-  `federation_version`: (`FederationVersion` = `LATEST_VERSION`) : You can use this to take a directive from a particular federation version

Note: The `federation_version` in `build_schema` is given higher priority. If the directive you have chosen is not compatible, it will raise an error

### Custom Directives

You can define custom directives as follows

```python
from graphene import Field, ObjectType, String
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull

from graphene_federation import ComposableDirective, DirectiveLocation, LATEST_VERSION
from graphene_federation import build_schema

CacheDirective = ComposableDirective(
    name="cache",
    locations=[DirectiveLocation.FIELD_DEFINITION, DirectiveLocation.OBJECT],
    args={
        "maxAge": GraphQLArgument(
            GraphQLNonNull(GraphQLInt), description="Specifies the maximum age for cache in seconds."
        ),
    },
    description="Caching directive to control cache behavior.",
    spec_url="https://specs.example.dev/directives/v1.0",
)

cache = CacheDirective.decorator()


@cache(max_age=20)
class Review(ObjectType):
    body = cache(field=String(), max_age=100)


class Query(ObjectType):
    review = Field(Review)


schema = build_schema(
    query=Query,
    directives=(CacheDirective,),
    federation_version=LATEST_VERSION ,
)
```

This will automatically add @link and @composeDirective to schema


```graphql
extend schema
	@link(url: "https://specs.apollo.dev/federation/v2.6", import: ["@composeDirective"])
	@link(url: "https://specs.example.dev/directives/v1.0", import: ["@cache"])
	@composeDirective(name: "@cache")

"""Caching directive to control cache behavior."""
directive @cache(
  """Specifies the maximum age for cache in seconds."""
  maxAge: Int!
) on FIELD_DEFINITION | OBJECT

type Query {
  review: Review
  _service: _Service!
}

type Review  @cache(maxAge: 20) {
  body: String @cache(maxAge: 100)
}
```

If you wish to add the schema_directives `@link` `@composeDirective` manually. 
You can pass the `add_to_schema_directives` as `False`

```python
from graphene import Field, ObjectType, String
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull

from graphene_federation import (ComposableDirective, DirectiveLocation, LATEST_VERSION, build_schema,
                                 compose_directive, link_directive)

CacheDirective = ComposableDirective(
    name="cache",
    locations=[DirectiveLocation.FIELD_DEFINITION, DirectiveLocation.OBJECT],
    args={
        "maxAge": GraphQLArgument(
            GraphQLNonNull(GraphQLInt), description="Specifies the maximum age for cache in seconds."
        ),
    },
    description="Caching directive to control cache behavior.",
    add_to_schema_directives=False
)

cache = CacheDirective.decorator()


@cache(max_age=20)
class Review(ObjectType):
    body = cache(field=String(), max_age=100)


class Query(ObjectType):
    review = Field(Review)


schema = build_schema(
    query=Query,
    directives=(CacheDirective,),
    schema_directives=(
        link_directive(url="https://specs.example.dev/directives/v1.0", import_=['@cache']),
        compose_directive(name='@cache'),
    ),
    federation_version=LATEST_VERSION,
)
```

### Custom field name

When using decorator on a field with custom name

####  Case 1 (auto_camelcase=False)

```python
@key("identifier")
@key("validEmail")
class User(ObjectType):
    identifier = ID()
    email = String(name="validEmail")

class Query(ObjectType):
    user = Field(User)

schema = build_schema(query=Query, federation_version=LATEST_VERSION, auto_camelcase=False) # Disable auto_camelcase
```

This works correctly.
By default `fields` of `@key`,`@requires` and `@provides` are not converted to camel case if `auto_camelcase` is set to `False`

#### Case 2 (auto_camelcase=True)
```python
@key("identifier")
@key("valid_email")
class User(ObjectType):
    identifier = ID()
    email = String(name="valid_email")

class Query(ObjectType):
    user = Field(User)

schema = build_schema(query=Query, federation_version=LATEST_VERSION) # auto_camelcase Enabled
```

This will raise an error `@key, field "validEmail" does not exist on type "User"`. 
Because The decorator auto camel-cased the `field` value of key, as schema has `auto_camelcase=True` (default)

To fix this, pass `auto_case=False` in the `@key`, `@requires` or `@provides` argument

```python
@key("identifier")
@key("valid_email", auto_case=False)
class User(ObjectType):
    identifier = ID()
    email = String(name="valid_email")

class Query(ObjectType):
    user = Field(User)

schema = build_schema(query=Query, federation_version=LATEST_VERSION) # auto_camelcase=True
```

------------------------

## Known Issues

- Using `@composeDirective` with `@link` in Federation `v2.6` shows error in rover, rover cli only supports upto `v2.5` as of 16/01/2024

## Contributing

* You can run the unit tests by doing: `make tests`.
* You can run the integration tests by doing `make integration-build && make integration-test`.
* You can get a development environment (on a Docker container) with `make dev-setup`.
* You should use `black` to format your code.

The tests are automatically run on Travis CI on push to GitHub.

---------------------------
