import json
from collections import defaultdict
from inspect import isawaitable
from typing import List

import graphene
from graphene import Schema
from graphql import (
    ArgumentNode,
    FieldNode,
    GraphQLField,
    GraphQLObjectType,
    GraphQLResolveInfo,
    ListValueNode,
    NameNode,
    ObjectValueNode,
    StringValueNode,
)
from graphql.pyutils import FrozenList, Path
from graphql_relay import from_global_id

from . import graphql_compatibility
from .utils import (
    field_name_to_type_attribute,
    get_data_for_id_filter_from_representations,
)


def copy_resolve_info(
    info: GraphQLResolveInfo,
    field_def: GraphQLField,
    field_nodes: List[FieldNode],
    parent_type: GraphQLObjectType,
    path: Path,
) -> GraphQLResolveInfo:
    """Build the GraphQLResolveInfo object.

    For internal use only."""
    # The resolve function's first argument is a collection of information about
    # the current execution state.
    return GraphQLResolveInfo(
        field_nodes[0].name.value,
        field_nodes,
        field_def.type,
        parent_type,
        path,
        info.schema,
        info.fragments,
        info.root_value,
        info.operation,
        info.variable_values,
        info.context,
        info.is_awaitable,
    )


def get_type_mapping(representations):
    type_mapping = defaultdict(list)

    for representation in representations:
        if isinstance(representation, ObjectValueNode):
            representation = {
                i.name.value: i.value.value for i in representation.fields
            }

        schema_name = representation["__typename"]
        type_mapping[schema_name].append(representation)

    return type_mapping


class BaseEntityQuery:
    _schema: Schema
    entities: graphene.List

    @classmethod
    async def resolve_entities(cls, obj, info: GraphQLResolveInfo, representations):
        entities = []
        type_mapping = get_type_mapping(representations)

        for schema_name, representations in type_mapping.items():
            type_ = graphql_compatibility.call_schema_get_type(cls._schema, schema_name)
            model = type_.graphene_type

            bulk_resolver = getattr(model, "_resolve_reference_bulk", None)
            if bulk_resolver:
                external_key, values = get_data_for_id_filter_from_representations(
                    model, representations
                )

                argument = ArgumentNode(
                    name=NameNode(value=f"{external_key}_In"),
                    value=ListValueNode(
                        values=[StringValueNode(value=r) for r in values]
                    ),
                )

                info.field_nodes[0].arguments = FrozenList([argument])
                setattr(info.context, "representation", model.__name__)
                result = bulk_resolver(model, info)

                if isawaitable(result):
                    result = await result

                results_dict = {}
                for edge in result.edges:
                    field = type_.fields[external_key]
                    fake_info = copy_resolve_info(
                        info,
                        field_def=field,
                        field_nodes=info.field_nodes,
                        parent_type=type_,
                        path=Path(info.path, 1, None),
                    )
                    k = field.resolve(edge.node, fake_info)

                    if isawaitable(k):
                        k = await k

                    results_dict[k] = edge.node

                for representation in representations:
                    entities.append(results_dict.get(representation[external_key]))

            else:
                for representation in representations:
                    model_arguments = representation.copy()
                    model_arguments.pop("__typename")
                    if graphql_compatibility.is_schema_in_auto_camelcase(cls._schema):
                        get_model_attr = field_name_to_type_attribute(
                            cls._schema, model
                        )
                        model_arguments = {
                            get_model_attr(k): v for k, v in model_arguments.items()
                        }

                    for k, v in model_arguments.items():
                        if isinstance(getattr(model, k, None), graphene.types.ID):
                            global_id = from_global_id(v)

                            assert (
                                global_id.type == schema_name
                            ), f"Invalid global id type: {schema_name} != {global_id.type}"

                            model_arguments[k] = json.loads(global_id.id)

                    model_instance = model(**model_arguments)
                    resolver = getattr(
                        model, "_%s__resolve_reference" % model.__name__, None
                    ) or getattr(model, "_resolve_reference", None)
                    if resolver:
                        model_instance = resolver(model_instance, info)

                    entities.append(model_instance)

        return entities
