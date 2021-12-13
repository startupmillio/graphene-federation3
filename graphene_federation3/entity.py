import json
from collections import defaultdict
from typing import Any, Dict, Union

import graphene
from graphene import List, Schema, Union
from graphql import ObjectValueNode
from graphql import ArgumentNode, NameNode, StringValueNode, ListValueNode
from graphql.pyutils import FrozenList
from graphql_relay import from_global_id

from . import graphql_compatibility
from .graphene_types import _Any
from .utils import (
    field_name_to_type_attribute,
    get_data_for_id_filter_from_representations,
)


def get_entities(schema: Schema) -> Dict[str, Any]:
    """
    Find all the entities from the schema.
    They can be easily distinguished from the other type as
    the `@key` and `@extend` decorators adds a `_sdl` attribute to them.
    """
    entities = {}
    for type_name, type_ in graphql_compatibility.get_type_map_from_schema(
        schema
    ).items():
        if not hasattr(type_, "graphene_type"):
            continue
        if getattr(type_.graphene_type, "_keys", None):
            entities[type_name] = type_.graphene_type
    return entities


def get_entity_cls(entities: Dict[str, Any]):
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
        entities = graphene.List(
            entity_type, name="_entities", representations=List(_Any)
        )

        async def resolve_entities(self, info, representations):
            entities = []
            type_mapping = defaultdict(list)
            for representation in representations:
                if isinstance(representation, ObjectValueNode):
                    representation = {
                        i.name.value: i.value.value for i in representation.fields
                    }

                schema_name = representation["__typename"]
                type_mapping[schema_name].append(representation)

            for schema_name, representations in type_mapping.items():
                type_ = graphql_compatibility.call_schema_get_type(schema, schema_name)
                model = type_.graphene_type

                bulk_resolver = getattr(model, "_resolve_reference_bulk", None)
                if bulk_resolver:
                    external_key, values = get_data_for_id_filter_from_representations(
                        model, representations
                    )
                    for representation in representations:
                        argument = ArgumentNode(
                            name=NameNode(value=f"{external_key}_Eq"),
                            value=StringValueNode(value=representation[external_key]),
                        )
                        info.field_nodes[0].arguments = FrozenList([argument])
                        setattr(info.context, "representation", model.__name__)
                        result = await bulk_resolver(model, info)
                        entities.extend([item.node for item in result.edges])
                else:
                    for representation in representations:
                        model_arguments = representation.copy()
                        model_arguments.pop("__typename")
                        if graphql_compatibility.is_schema_in_auto_camelcase(schema):
                            get_model_attr = field_name_to_type_attribute(schema, model)
                            model_arguments = {
                                get_model_attr(k): v for k, v in model_arguments.items()
                            }

                        for k, v in model_arguments.items():
                            if isinstance(getattr(model, k, None), graphene.types.ID):
                                global_id = from_global_id(v)

                                assert (
                                    global_id.type == schema_name
                                ), f"Invalid global id type: {schema_name} != {global_id}"

                                model_arguments[k] = json.loads(global_id.id)

                        model_instance = model(**model_arguments)
                        resolver = getattr(
                            model, "_%s__resolve_reference" % model.__name__, None
                        ) or getattr(model, "_resolve_reference", None)
                        if resolver:
                            model_instance = resolver(model_instance, info)

                        entities.append(model_instance)

            return entities

    return EntityQuery


def key(fields: str):
    """
    Take as input a field that should be used as key for that entity.
    See specification: https://www.apollographql.com/docs/federation/federation-spec/#key

    If the input contains a space it means it's a [compound primary key](https://www.apollographql.com/docs/federation/entities/#defining-a-compound-primary-key)
    which is not yet supported.
    """
    if " " in fields:
        raise NotImplementedError("Compound primary keys are not supported.")

    def decorator(Type):
        # Check the provided fields actually exist on the Type.
        assert (
            fields in Type._meta.fields
        ), f'Field "{fields}" does not exist on type "{Type._meta.name}"'

        keys = getattr(Type, "_keys", [])
        keys.append(fields)
        setattr(Type, "_keys", keys)

        return Type

    return decorator
