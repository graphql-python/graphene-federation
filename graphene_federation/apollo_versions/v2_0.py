from graphene_directives import CustomDirective, DirectiveLocation
from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLDirective,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_federation.scalars import FieldSet
from graphene_federation.transform import field_set_case_transform
from graphene_federation.validators import (
    validate_key,
    validate_provides,
    validate_requires,
)
from .v1_0 import extends_directive

key_directive = CustomDirective(
    name="key",
    locations=[
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
    ],
    args={
        "fields": GraphQLArgument(GraphQLNonNull(FieldSet)),
        # Changed from v1.0
        "resolvable": GraphQLArgument(GraphQLBoolean, default_value=True),
    },
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
    args={
        "fields": GraphQLArgument(GraphQLNonNull(FieldSet))
    },  # Changed _FieldSet -> FieldSet
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
    args={
        "fields": GraphQLArgument(GraphQLNonNull(FieldSet))
    },  # Changed _FieldSet -> FieldSet
    description="Federation @provides directive",
    add_definition_to_schema=False,
    field_validator=validate_provides,
    input_transform=field_set_case_transform,
)


external_directive = CustomDirective(
    name="external",
    locations=[
        DirectiveLocation.OBJECT,  # Changed from v1.0
        DirectiveLocation.FIELD_DEFINITION,
    ],
    description="Federation @external directive",
    add_definition_to_schema=False,
)


shareable_directive = CustomDirective(
    name="shareable",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
    ],
    description="Federation @shareable directive",
    add_definition_to_schema=False,
)


override_directive = CustomDirective(
    name="override",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
    ],
    args={
        "from": GraphQLArgument(GraphQLNonNull(GraphQLString)),
    },
    description="Federation @override directive",
    add_definition_to_schema=False,
)

inaccessible_directive = CustomDirective(
    name="inaccessible",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
        DirectiveLocation.UNION,
        DirectiveLocation.ENUM,
        DirectiveLocation.ENUM_VALUE,
        DirectiveLocation.SCALAR,
        DirectiveLocation.INPUT_OBJECT,
        DirectiveLocation.INPUT_FIELD_DEFINITION,
        DirectiveLocation.ARGUMENT_DEFINITION,
    ],
    description="Federation @inaccessible directive",
    add_definition_to_schema=False,
)

tag_directive = CustomDirective(
    name="tag",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.INTERFACE,
        DirectiveLocation.OBJECT,
        DirectiveLocation.UNION,
        DirectiveLocation.ARGUMENT_DEFINITION,
        DirectiveLocation.SCALAR,
        DirectiveLocation.ENUM,
        DirectiveLocation.ENUM_VALUE,
        DirectiveLocation.INPUT_OBJECT,
        DirectiveLocation.INPUT_FIELD_DEFINITION,
    ],
    description="Federation @tag directive",
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
            shareable_directive,
            extends_directive,  # From v1.0
            override_directive,
            inaccessible_directive,
            tag_directive,
        ]
    }
