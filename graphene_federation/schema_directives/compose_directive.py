from graphene_directives import SchemaDirective

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)


def compose_directive(
    name: str,
    federation_version: FederationVersion = LATEST_VERSION,
) -> SchemaDirective:
    """
    Indicates to composition that all uses of a particular custom type system directive in the subgraph schema should be
    preserved in the supergraph schema

    (by default, composition omits most directives from the supergraph schema).

    Use this in the `schema_directives` argument of `build_schema`

    It is not recommended to use this directive directly, instead use the ComposableDirective class to build
    a custom directive. It will automatically add the compose and link directive to schema

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#composedirective
    """
    directive = get_directive_from_name("composeDirective", federation_version)
    return SchemaDirective(
        target_directive=directive,
        arguments={"name": name},
    )
