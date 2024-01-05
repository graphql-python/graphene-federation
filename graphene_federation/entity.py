from __future__ import annotations

import collections.abc
from typing import Any, Callable, Dict

from graphene import Field, List, NonNull, ObjectType, Union
from graphene.types.schema import Schema
from graphene.types.schema import TypeMap

from .types import _Any
from .utils import (
    check_fields_exist_on_type,
    field_name_to_type_attribute,
    is_valid_compound_key,
)


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def get_entities(schema: Schema) -> Dict[str, Any]:
    """
    Find all the entities from the type map.
    They can be easily distinguished from the other type as
    the `@key` and `@extend` decorators adds a `_sdl` attribute to them.
    """
    type_map: TypeMap = schema.graphql_schema.type_map
    entities = {}
    for type_name, type_ in type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        if getattr(type_.graphene_type, "_keys", None):
            entities[type_name] = type_.graphene_type

            # Validation for compound keys
            key_str = " ".join(type_.graphene_type._keys)
            type_name = type_.graphene_type._meta.name
            if "{" in key_str:  # checking for subselection to identify compound key
                assert is_valid_compound_key(
                    type_name, key_str, schema
                ), f'Invalid compound key definition for type "{type_name}"'
    return entities


def get_entity_cls(entities: Dict[str, Any]) -> Union:
    """
    Create _Entity type which is a union of all the entities types.
    """

    class _Entity(Union):
        class Meta:
            types = tuple(entities.values())

    return _Entity


def get_entity_query(schema: Schema):
    """
    Create Entity query.
    """
    entities_dict = get_entities(schema)
    if not entities_dict:
        return

    entity_type = get_entity_cls(entities_dict)

    class EntityQuery:
        entities = List(
            entity_type,
            name="_entities",
            representations=NonNull(List(NonNull(_Any))),
            required=True,
        )

        def resolve_entities(self, info, representations, sub_field_resolution=False):
            entities = []
            for representation in representations:
                type_ = schema.graphql_schema.get_type(representation["__typename"])
                model = type_.graphene_type
                model_arguments = representation.copy()
                model_arguments.pop("__typename")
                if schema.auto_camelcase:
                    get_model_attr = field_name_to_type_attribute(schema, model)
                    model_arguments = {
                        get_model_attr(k): v for k, v in model_arguments.items()
                    }

                # convert subfields of models from dict to a corresponding graphql type
                for model_field, value in model_arguments.items():
                    if not hasattr(model, model_field):
                        continue

                    field = getattr(model, model_field)
                    if isinstance(field, Field) and isinstance(value, dict):
                        if value.get("__typename") is None:
                            value["__typename"] = field.type.of_type._meta.name
                        model_arguments[model_field] = EntityQuery.resolve_entities(
                            self,
                            info,
                            representations=[value],
                            sub_field_resolution=True,
                        ).pop()
                    elif all(
                        [
                            isinstance(field, List),
                            isinstance(value, list),
                            any(
                                [
                                    (
                                        hasattr(field, "of_type")
                                        and issubclass(field.of_type, ObjectType)
                                    ),
                                    (
                                        hasattr(field, "of_type")
                                        and issubclass(field.of_type, Union)
                                    ),
                                ]
                            ),
                        ]
                    ):
                        for sub_value in value:
                            if sub_value.get("__typename") is None:
                                sub_value["__typename"] = field.type.of_type._meta.name
                        model_arguments[model_field] = EntityQuery.resolve_entities(
                            self, info, representations=value, sub_field_resolution=True
                        )

                model_instance = model(**model_arguments)

                resolver = getattr(
                    model, "_%s__resolve_reference" % model.__name__, None
                ) or getattr(model, "_resolve_reference", None)
                if resolver and not sub_field_resolution:
                    model_instance = resolver(model_instance, info)

                entities.append(model_instance)
            return entities

    return EntityQuery


def key(fields: str, resolvable: bool = True) -> Callable:
    """
    Take as input a field that should be used as key for that entity.
    See specification: https://www.apollographql.com/docs/federation/federation-spec/#key
    """

    def decorator(type_):
        # Check the provided fields actually exist on the Type.
        if " " not in fields:
            assert (
                fields in type_._meta.fields
            ), f'Field "{fields}" does not exist on type "{type_._meta.name}"'
        if "{" not in fields:
            # Skip valid fields check if the key is a compound key. The validation for compound keys
            # is done on calling get_entities()
            fields_set = set(fields.split(" "))
            assert check_fields_exist_on_type(
                fields=fields_set, type_=type_
            ), f'Field "{fields}" does not exist on type "{type_._meta.name}"'

        keys = getattr(type_, "_keys", [])
        keys.append(fields)
        setattr(type_, "_keys", keys)
        setattr(type_, "_resolvable", resolvable)

        return type_

    return decorator
