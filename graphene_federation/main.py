from typing import Collection, Type, Union
from typing import Optional

from graphene import ObjectType, PageInfo
from graphene_directives import (
    SchemaDirective,
    build_schema as build_directive_schema,
    directive_decorator,
)
from graphene_directives.schema import Schema

from . import FederationDirective
from .apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
    get_directives_based_on_version,
)
from .apollo_versions.v2_1 import compose_directive as ComposeDirective
from .entity import get_entity_query
from .schema_directives import compose_directive, link_directive
from .service import get_service_query


def _get_query(
    schema: Schema, query_cls: Optional[ObjectType] = None
) -> Type[ObjectType]:
    type_name = "Query"
    bases = [get_service_query(schema)]
    entity_cls = get_entity_query(schema)
    if entity_cls:
        bases.append(entity_cls)
    if query_cls is not None:
        type_name = query_cls.__name__
        bases.append(query_cls)
    federated_query_cls = type(type_name, tuple(bases), {})
    return federated_query_cls  # noqa


def build_schema(
    query: Union[ObjectType, Type[ObjectType]] = None,
    mutation: Union[ObjectType, Type[ObjectType]] = None,
    subscription: Union[ObjectType, Type[ObjectType]] = None,
    types: Collection[Union[ObjectType, Type[ObjectType]]] = None,
    directives: Union[Collection[FederationDirective], None] = None,
    include_graphql_spec_directives: bool = True,
    schema_directives: Collection[SchemaDirective] = None,
    auto_camelcase: bool = True,
    enable_federation_2: bool = False,
    federation_version: FederationVersion = None,
) -> Schema:
    """
    Build Schema.

    Args:
        query (Type[ObjectType]): Root query *ObjectType*. Describes entry point for fields to *read*
            data in your Schema.
        mutation (Optional[Type[ObjectType]]): Root mutation *ObjectType*. Describes entry point for
            fields to *create, update or delete* data in your API.
        subscription (Optional[Type[ObjectType]]): Root subscription *ObjectType*. Describes entry point
            for fields to receive continuous updates.
        types (Optional[Collection[Type[ObjectType]]]): List of any types to include in schema that
            may not be introspected through root types.
        directives (List[GraphQLDirective], optional): List of custom directives to include in the
            GraphQL schema.
        auto_camelcase (bool): Fieldnames will be transformed in Schema's TypeMap from snake_case
            to camelCase (preferred by GraphQL standard). Default True.
        schema_directives (Collection[SchemaDirective]): Directives that can be defined at DIRECTIVE_LOCATION.SCHEMA
            with their argument values.
        include_graphql_spec_directives (bool): Includes directives defined by GraphQL spec (@include, @skip,
            @deprecated, @specifiedBy)
        enable_federation_2 (bool): Whether to enable federation 2 directives (default False)
        federation_version (FederationVersion): Specify the version explicit (default LATEST_VERSION)

        In case both enable_federation_2 and federation_version are specified, federation_version is given
        higher priority
    """

    federation_version = (
        federation_version
        if federation_version
        else LATEST_VERSION
        if enable_federation_2
        else FederationVersion.VERSION_1_0
    )
    enable_federation_2 = federation_version.value > FederationVersion.VERSION_1_0.value

    _types = list(types) if types is not None else []

    _directives = get_directives_based_on_version(federation_version)
    federation_directives = set(_directives.keys())
    if directives is not None:
        _directives.update({directive.name: directive for directive in directives})

    schema_args = {
        "mutation": mutation,
        "subscription": subscription,
        "types": _types,
        "directives": _directives.values(),
        "auto_camelcase": auto_camelcase,
        "include_graphql_spec_directives": include_graphql_spec_directives,
    }

    schema: Schema = build_directive_schema(query=query, **schema_args)

    if "PageInfo" in schema.graphql_schema.type_map:
        # PageInfo needs @sharable directive
        try:
            sharable = get_directive_from_name("shareable", federation_version)

            _types.append(
                directive_decorator(target_directive=sharable)(field=None)(PageInfo)
            )
        except ValueError:
            # Federation Version does not support @sharable
            pass

    _schema_directives = []
    directives_used = schema.get_directives_used()
    if schema_directives or directives:
        if not enable_federation_2:
            raise ValueError(
                f"Schema Directives & Directives are not supported on {federation_version=}. Use >=2.0 "
            )

        if (
            any(
                schema_directive.target_directive == ComposeDirective
                for schema_directive in schema_directives or []
            )
            or directives
        ):
            directives_used.append(ComposeDirective)

    if directives_used and enable_federation_2:
        imports = [
            str(directive)
            for directive in directives_used
            if directive.name in federation_directives
        ]
        if imports:
            _schema_directives.append(
                link_directive(
                    url=f"https://specs.apollo.dev/federation/v{federation_version.value}",
                    import_=sorted(imports),
                )
            )

    if directives:
        url__imports: dict[str, list[str]] = {}
        for directive in directives:
            assert isinstance(
                directive, FederationDirective
            ), "directives must be of instance FederationDirective"

            if not directive.add_to_schema_directives:
                continue

            _imports = url__imports.get(directive.spec_url)
            if _imports:
                _imports.append(str(directive))
            else:
                url__imports[directive.spec_url] = [str(directive)]

        for spec, imports in url__imports.items():
            _schema_directives.append(link_directive(url=spec, import_=sorted(imports)))

        for directive in directives:
            if not directive.add_to_schema_directives:
                continue
            _schema_directives.append(compose_directive(name=str(directive)))

    if schema_directives:
        _schema_directives.extend(list(schema_directives))

    schema_args["schema_directives"] = _schema_directives if enable_federation_2 else []
    schema = build_directive_schema(query=query, **schema_args)
    return build_directive_schema(query=_get_query(schema, schema.query), **schema_args)
