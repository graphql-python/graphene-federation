from graphql import GraphQLDirective

from .v1_0 import get_directives as get_directives_v1_0
from .v2_0 import get_directives as get_directives_v2_0
from .v2_1 import get_directives as get_directives_v2_1
from .v2_2 import get_directives as get_directives_v2_2
from .v2_3 import get_directives as get_directives_v2_3
from .version import FederationVersion

LATEST_VERSION = FederationVersion.VERSION_2_3


def get_directives_based_on_version(
    federation_version: FederationVersion,
) -> dict[str, GraphQLDirective]:
    match federation_version:
        case FederationVersion.VERSION_1_0:
            return get_directives_v1_0()
        case FederationVersion.VERSION_2_0:
            return get_directives_v2_0()
        case FederationVersion.VERSION_2_1:
            return get_directives_v2_1()
        case FederationVersion.VERSION_2_2:
            return get_directives_v2_2()
        case FederationVersion.VERSION_2_3:
            return get_directives_v2_3()
        case _:
            return get_directives_v2_3()


def get_directive_from_name(
    directive_name: str, federation_version: FederationVersion
) -> GraphQLDirective:
    directive = get_directives_based_on_version(federation_version).get(
        directive_name, None
    )
    if directive is None:
        raise ValueError(
            f"@{directive_name} not supported on federation version {federation_version}"
        )
    return directive
