import re
from typing import List

from graphene.types.interface import InterfaceOptions
from graphene.types.union import UnionOptions
from graphql import GraphQLInterfaceType, GraphQLObjectType

from .external import get_external_fields
from .inaccessible import get_inaccessible_types, get_inaccessible_fields
from .override import get_override_fields
from .requires import get_required_fields
from .shareable import get_shareable_types, get_shareable_fields
from graphql.utilities.print_schema import print_fields

from graphene import ObjectType, String, Field, Schema

from .extend import get_extended_types
from .provides import get_provides_parent_types, get_provides_fields

from .entity import get_entities
from .tag import get_tagged_fields
from .utils import field_name_to_type_attribute, type_attribute_to_field_name


class MonoFieldType:
    """
    In order to be able to reuse the `print_fields` method to get a singular field
    string definition, we need to define an object that has a `.fields` attribute.
    """

    def __init__(self, name, field):
        self.fields = {name: field}


def convert_fields(schema: Schema, fields: List[str]) -> str:
    get_field_name = type_attribute_to_field_name(schema)
    return " ".join([get_field_name(field) for field in fields])


DECORATORS = {
    "_external": lambda schema, fields: "@external",
    "_requires": lambda schema, fields: f'@requires(fields: "{convert_fields(schema, fields)}")',
    "_provides": lambda schema, fields: f'@provides(fields: "{convert_fields(schema, fields)}")',
    "_shareable": lambda schema, fields: "@shareable",
    "_inaccessible": lambda schema, fields: "@inaccessible",
    "_override": lambda schema, from_: f'@override(from: "{from_}")',
    "_tag": lambda schema, name: f'@tag(name: "{name}")',
}


def field_to_string(field) -> str:
    str_field = print_fields(field)
    # Remove blocks added by `print_block`
    block_match = re.match(r" \{\n(?P<field_str>.*)\n\}", str_field, flags=re.DOTALL)
    if block_match:
        str_field = block_match.groups()[0]
    return str_field


def add_entity_fields_decorators(entity, schema: Schema, string_schema: str) -> str:
    """
    For a given entity, go through all its fields and see if any directive decorator need to be added.
    The methods (from graphene-federation) marking fields that require some special treatment for federation add
    corresponding attributes to the field itself.
    Those attributes are listed in the `DECORATORS` variable as key and their respective value is the resolver that
    returns what needs to be amended to the field declaration.

    This method simply go through the fields that need to be modified and replace them with their annotated version in the
    schema string representation.
    """
    entity_name = entity._meta.name
    entity_type = schema.graphql_schema.get_type(entity_name)
    str_fields = []
    get_model_attr = field_name_to_type_attribute(schema, entity)
    for field_name, field in (
        entity_type.fields.items() if getattr(entity_type, "fields", None) else []
    ):
        str_field = field_to_string(MonoFieldType(field_name, field))
        # Check if we need to annotate the field by checking if it has the decorator attribute set on the field.
        f = getattr(entity, get_model_attr(field_name), None)
        if f is not None:
            for decorator, decorator_resolver in DECORATORS.items():
                decorator_value = getattr(f, decorator, None)
                if decorator_value:
                    str_field += f" {decorator_resolver(schema, decorator_value)}"
        str_fields.append(str_field)
    str_fields_annotated = "\n".join(str_fields)
    # Replace the original field declaration by the annotated one
    if isinstance(entity_type, GraphQLObjectType) or isinstance(
        entity_type, GraphQLInterfaceType
    ):
        str_fields_original = field_to_string(entity_type)
    else:
        str_fields_original = ""
    pattern = re.compile(
        r"(type\s%s\s[^\{]*)\{\s*%s\s*\}"
        % (entity_name, re.escape(str_fields_original))
    )
    string_schema = pattern.sub(r"\g<1> {\n%s\n}" % str_fields_annotated, string_schema)
    return string_schema


def get_sdl(schema: Schema) -> str:
    """
    Add all needed decorators to the string representation of the schema.
    """

    string_schema = str(schema)

    regex = r"schema \{(\w|\!|\s|\:)*\}"
    pattern = re.compile(regex)
    string_schema = pattern.sub(" ", string_schema)

    # Get various objects that need to be amended
    extended_types = get_extended_types(schema)
    provides_parent_types = get_provides_parent_types(schema)
    provides_fields = get_provides_fields(schema)
    entities = get_entities(schema)
    required_fields = get_required_fields(schema)
    external_fields = get_external_fields(schema)
    override_fields = get_override_fields(schema)

    _schema = ""

    if schema.federation_version == 2:
        shareable_types = get_shareable_types(schema)
        inaccessible_types = get_inaccessible_types(schema)
        shareable_fields = get_shareable_fields(schema)
        tagged_fields = get_tagged_fields(schema)
        inaccessible_fields = get_inaccessible_fields(schema)

        _schema_import = []

        if extended_types:
            _schema_import.append('"@extends"')
        if external_fields:
            _schema_import.append('"@external"')
        if entities:
            _schema_import.append('"@key"')
        if override_fields:
            _schema_import.append('"@override"')
        if provides_parent_types or provides_fields:
            _schema_import.append('"@provides"')
        if required_fields:
            _schema_import.append('"@requires"')
        if inaccessible_types or inaccessible_fields:
            _schema_import.append('"@inaccessible"')
        if shareable_types or shareable_fields:
            _schema_import.append('"@shareable"')
        if tagged_fields:
            _schema_import.append('"@tag"')
        schema_import = ", ".join(_schema_import)
        _schema = f'extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: [{schema_import}])\n'

    # Add fields directives (@external, @provides, @requires, @shareable, @inaccessible)
    entities_ = (
        set(provides_parent_types.values())
        | set(extended_types.values())
        | set(entities.values())
        | set(required_fields.values())
        | set(provides_fields.values())
    )

    if schema.federation_version == 2:
        entities_ = (
            entities_
            | set(shareable_types.values())
            | set(inaccessible_types.values())
            | set(inaccessible_fields.values())
            | set(shareable_fields.values())
            | set(tagged_fields.values())
        )
    for entity in entities_:
        string_schema = add_entity_fields_decorators(entity, schema, string_schema)

    # Prepend `extend` keyword to the type definition of extended types
    # noinspection DuplicatedCode
    for entity_name, entity in extended_types.items():
        type_def = re.compile(rf"type {entity_name} ([^{{]*)")
        repl_str = rf"extend type {entity_name} \1"
        string_schema = type_def.sub(repl_str, string_schema)

    # Add entity keys declarations
    get_field_name = type_attribute_to_field_name(schema)
    for entity_name, entity in entities.items():
        type_def_re = rf"(type {entity_name} [^\{{]*)" + " "

        # resolvable argument of @key directive is true by default. If false, we add 'resolvable: false' to sdl.
        if (
            schema.federation_version == 2
            and hasattr(entity, "_resolvable")
            and not entity._resolvable
        ):
            type_annotation = (
                (
                    " ".join(
                        [
                            f'@key(fields: "{get_field_name(key)}"'
                            for key in entity._keys
                        ]
                    )
                )
                + f", resolvable: {str(entity._resolvable).lower()})"
                + " "
            )
        else:
            type_annotation = (
                " ".join(
                    [f'@key(fields: "{get_field_name(key)}")' for key in entity._keys]
                )
            ) + " "
        repl_str = rf"\1{type_annotation}"
        pattern = re.compile(type_def_re)
        string_schema = pattern.sub(repl_str, string_schema)

    if schema.federation_version == 2:
        for type_name, type in shareable_types.items():
            # noinspection PyProtectedMember
            if isinstance(type._meta, UnionOptions):
                type_def_re = rf"(union {type_name})"
            else:
                type_def_re = rf"(type {type_name} [^\{{]*)" + " "
            type_annotation = " @shareable"
            repl_str = rf"\1{type_annotation} "
            pattern = re.compile(type_def_re)
            string_schema = pattern.sub(repl_str, string_schema)

        for type_name, type in inaccessible_types.items():
            # noinspection PyProtectedMember
            if isinstance(type._meta, InterfaceOptions):
                type_def_re = rf"(interface {type_name}[^\{{]*)" + " "
            elif isinstance(type._meta, UnionOptions):
                type_def_re = rf"(union {type_name})"
            else:
                type_def_re = rf"(type {type_name} [^\{{]*)" + " "
            type_annotation = " @inaccessible"
            repl_str = rf"\1{type_annotation} "
            pattern = re.compile(type_def_re)
            string_schema = pattern.sub(repl_str, string_schema)

    return _schema + string_schema


def get_service_query(schema: Schema):
    sdl_str = get_sdl(schema)

    class _Service(ObjectType):
        sdl = String()

        def resolve_sdl(parent, _):
            return sdl_str

    class ServiceQuery(ObjectType):
        _service = Field(_Service, name="_service", required=True)

        def resolve__service(parent, info):
            return _Service()

    return ServiceQuery
