from typing import Any, Callable

import graphene
from graphene import Schema
from graphene.utils.str_converters import to_camel_case

from graphene_federation3 import graphql_compatibility


def field_name_to_type_attribute(schema: Schema, model: Any) -> Callable[[str], str]:
    """
    Create field name conversion method (from schema name to actual graphene_type attribute name).
    """
    field_names = {}
    if graphql_compatibility.is_schema_in_auto_camelcase(schema):
        field_names = {
            to_camel_case(attr_name): attr_name for attr_name in model._meta.fields
        }
    return lambda schema_field_name: field_names.get(
        schema_field_name, schema_field_name
    )


def type_attribute_to_field_name(schema: Schema) -> Callable[[str], str]:
    """
    Create a conversion method to convert from graphene_type attribute name to the schema field name.
    """

    if graphql_compatibility.is_schema_in_auto_camelcase(schema):
        return lambda attr_name: to_camel_case(attr_name)
    else:
        return lambda attr_name: attr_name


def get_data_for_id_filter_from_representations(
    object_type: graphene.Field, representations: list
):
    if getattr(object_type, "_keys", None):
        keys = getattr(object_type, "_keys")
        for key in keys:
            key = to_camel_case(key)
            if key in representations[0]:
                return key, [r[key] for r in representations]
