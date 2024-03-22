from graphql import GraphQLDirective

from .v2_3 import get_directives as get_directives_v2_3


# No Change, Added Subscription Support
def get_directives() -> dict[str, GraphQLDirective]:
    return get_directives_v2_3()
