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

At the moment it supports:

* `sdl` (`_service` on field): enable to add schema in federation (as is)
* `@key` decorator (entity support): enable to perform queries across service boundaries (you can have more than one key per type)
* `@extend`: extend remote types
* `external()`: mark a field as external
* `requires()`: mark that field resolver requires other fields to be pre-fetched
* `provides()`/`@provides`: annotate the expected returned fieldset from a field on a base type that is guaranteed to be selectable by the gateway.

Each type which is decorated with `@key` or `@extend` is added to the `_Entity` union.
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
from graphene import Field, ID, ObjectType, String
from graphene_federation import build_schema, key

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

schema = build_schema(query=Query)
```

### Product
The product service exposes a `Product` type that can be used by other services via the `upc` field:

```python
from graphene import Argument, ID, Int, List, ObjectType, String
from graphene_federation import build_schema, key

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

schema = build_schema(query=Query)
```

### Reviews
The reviews service exposes a `Review` type which has a link to both the `User` and `Product` types.
It also has the ability to provide the username of the `User`.
On top of that it adds to the `User`/`Product` types (that are both defined in other services) the ability to get their reviews.

```python
from graphene import Field, ID, Int, List, ObjectType, String
from graphene_federation import build_schema, extend, external, provides

@extend("id")
class User(ObjectType):
    id = external(Int(required=True))
    reviews = List(lambda: Review)

    def resolve_reviews(self, info, *args, **kwargs):
        """
        Get all the reviews of a given user. (not implemented here)
        """
        return []

@extend("upc")
class Product(ObjectType):
    upc = external(String(required=True))
    reviews = List(lambda: Review)

# Note that both the base type and the field need to be decorated with `provides` (on the field itself you need to specify which fields get provided).
@provides
class Review(ObjectType):
    body = String()
    author = provides(Field(User), fields="username")
    product = Field(Product)

class Query(ObjectType):
    review = Field(Review)

schema = build_schema(query=Query)
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

## Known issues

1. decorators will not work properly on fields with custom names for example `some_field = String(name='another_name')`

------------------------

## Contributing

* You can run the unit tests by doing: `make tests`.
* You can run the integration tests by doing `make integration-build && make integration-test`.
* You can get a development environment (on a Docker container) with `make dev-setup`.
* You should use `black` to format your code.

The tests are automatically run on Travis CI on push to GitHub.

---------------------------
