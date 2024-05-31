from graphene_directives import CustomDirective, DirectiveLocation
from graphql import GraphQLArgument, GraphQLDirective, GraphQLList, GraphQLNonNull

from .v2_5 import get_directives as get_directives_v2_5
from graphene_federation.scalars import FederationPolicy

policy_directive = CustomDirective(
    name="policy",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
        DirectiveLocation.SCALAR,
        DirectiveLocation.ENUM,
    ],
    args={
        "policies": GraphQLArgument(
            GraphQLNonNull(
                GraphQLList(
                    GraphQLNonNull(GraphQLList(GraphQLNonNull(FederationPolicy)))
                )
            )
        ),
    },
    description="Federation @policy directive",
    add_definition_to_schema=False,
)


# No Change, Added Subscription Support
def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_5()
    directives.update({directive.name: directive for directive in [policy_directive]})
    return directives
