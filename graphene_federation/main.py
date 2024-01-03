from typing import Optional

from graphene import Schema
from graphene import ObjectType

from .entity import get_entity_query
from .service import get_service_query


def _get_query(schema: Schema, query_cls: Optional[ObjectType] = None) -> ObjectType:
    type_name = "Query"
    bases = [get_service_query(schema)]
    entity_cls = get_entity_query(schema)
    if entity_cls:
        bases.append(entity_cls)
    if query_cls is not None:
        type_name = query_cls.__name__
        bases.append(query_cls)
    federated_query_cls = type(type_name, tuple(bases), {})
    return federated_query_cls


def build_schema(
    query: Optional[ObjectType] = None,
    mutation: Optional[ObjectType] = None,
    federation_version: Optional[float] = None,
    enable_federation_2: bool = False,
    schema: Optional[Schema] = None,
    **kwargs
) -> Schema:
    schema = schema or Schema(query=query, mutation=mutation, **kwargs)
    schema.auto_camelcase = kwargs.get("auto_camelcase", True)
    schema.federation_version = float(
        (federation_version or 2) if (enable_federation_2 or federation_version) else 1
    )
    federation_query = _get_query(schema, schema.query)
    # Use shallow copy to prevent recursion error
    kwargs = schema.__dict__.copy()
    kwargs.pop("query")
    kwargs.pop("graphql_schema")
    kwargs.pop("federation_version")
    return type(schema)(query=federation_query, **kwargs)
