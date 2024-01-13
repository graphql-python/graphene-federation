from graphene_directives import SchemaDirective

from ..appolo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name


def compose_directive(
    name: str,
    federation_version: FederationVersion = LATEST_VERSION,
) -> SchemaDirective:
    directive = get_directive_from_name("composeDirective", federation_version)
    return SchemaDirective(
        target_directive=directive,
        arguments={"name": name},
    )
