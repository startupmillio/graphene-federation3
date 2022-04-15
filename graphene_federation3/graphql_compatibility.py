"""
Allows the project to interact to graphql using both graphene 2.1.8 and 3.0.0b7.
Other function to preserve backwards compatibiolity may be added in the future
"""
from typing import Dict, Optional

from graphene import Schema
from graphene.types.schema import TypeMap
from graphql import GraphQLSchema
from graphql.utilities.print_schema import (
    print_args,
    print_deprecated,
    print_description,
    print_schema,
)


def assert_schema_is(actual: Schema, expected_3: str):
    actual_str = get_schema_str(actual)
    assert (
        actual_str == expected_3
    ), f"\n{actual_str}\n!=\n{expected_3}\nDIFFERENCES: {list(filter(lambda x: x[1][0] != x[1][1], enumerate(zip(actual_str.strip(), expected_3.strip()))))}"


def assert_graphql_response_data(actual: str, expected_3: str):
    assert (
        actual.strip() == expected_3.strip()
    ), f"\n{actual.strip()}\n!=\n{expected_3.strip()}\nDIFFERENCES: {list(filter(lambda x: x[1][0] != x[1][1], enumerate(zip(actual.strip(), expected_3.strip()))))}"


def call_schema_print_fields(schema: Schema, t: type) -> str:
    # copy of print_fields from graphene 3.0.0 where we avoid calling print_blocks
    fields = [
        print_description(field, "  ", not i)
        + f"  {name}"
        + print_args(field.args, "  ")
        + f": {field.type}"
        + print_deprecated(field.deprecation_reason)
        for i, (name, field) in enumerate(t.fields.items())
    ]
    return "\n".join(fields)


def get_schema_str(schema: Schema) -> str:
    def print_schema_definition_forced(
        schema: GraphQLSchema,
    ) -> Optional[str]:
        # picked from print_schema_definition and removed the early return
        operation_types = []

        query_type = schema.query_type
        if query_type:
            operation_types.append(f"  query: {query_type.name}")

        mutation_type = schema.mutation_type
        if mutation_type:
            operation_types.append(f"  mutation: {mutation_type.name}")

        subscription_type = schema.subscription_type
        if subscription_type:
            operation_types.append(f"  subscription: {subscription_type.name}")

        return "schema {\n" + "\n".join(operation_types) + "\n}"

    result = (
        print_schema_definition_forced(schema.graphql_schema)
        + "\n\n"
        + print_schema(schema.graphql_schema)
    )
    return result


def get_type_map_from_schema(schema: Schema) -> TypeMap:
    return schema.graphql_schema.type_map


def call_schema_get_type(schema: Schema, name: str) -> Optional["GraphQLNamedType"]:
    return schema.graphql_schema.get_type(name)


def is_schema_in_auto_camelcase(schema: Schema) -> bool:
    # I don't know a method to detect whether auto_camelcase has been activated in graphene. Generating the default
    # To manage that, I hardcoded the auto_camelcase when creating the schema, since such information is not stored
    # in the datastructures of graphene (AFAIK)
    if hasattr(schema, "auto_camelcase"):
        return schema.auto_camelcase
    else:
        # Otherwise we trat it as the camel case is set
        return True
