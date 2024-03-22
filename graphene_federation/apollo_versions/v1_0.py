from graphene_directives import CustomDirective, DirectiveLocation
from graphql import GraphQLArgument, GraphQLDirective, GraphQLNonNull

from graphene_federation.scalars import _FieldSet
from graphene_federation.transform import field_set_case_transform
from graphene_federation.validators import (
    validate_key,
    validate_provides,
    validate_requires,
)

key_directive = CustomDirective(
    name="key",
    locations=[
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
    ],
    args={"fields": GraphQLArgument(GraphQLNonNull(_FieldSet))},
    description="Federation @key directive",
    is_repeatable=True,
    add_definition_to_schema=False,
    non_field_validator=validate_key,
    input_transform=field_set_case_transform,
)

requires_directive = CustomDirective(
    name="requires",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
    ],
    args={"fields": GraphQLArgument(GraphQLNonNull(_FieldSet))},
    description="Federation @requires directive",
    add_definition_to_schema=False,
    field_validator=validate_requires,
    input_transform=field_set_case_transform,
)


provides_directive = CustomDirective(
    name="provides",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
    ],
    args={"fields": GraphQLArgument(GraphQLNonNull(_FieldSet))},
    description="Federation @provides directive",
    add_definition_to_schema=False,
    field_validator=validate_provides,
    input_transform=field_set_case_transform,
)

external_directive = CustomDirective(
    name="external",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
    ],
    description="Federation @external directive",
    add_definition_to_schema=False,
)

extends_directive = CustomDirective(
    name="extends",
    locations=[
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
    ],
    description="Federation @extends directive",
    add_definition_to_schema=False,
)


def get_directives() -> dict[str, GraphQLDirective]:
    return {
        directive.name: directive
        for directive in [
            key_directive,
            requires_directive,
            provides_directive,
            external_directive,
            extends_directive,
        ]
    }
