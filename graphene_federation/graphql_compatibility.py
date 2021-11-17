"""
Allows the project to interact to graphql using both graphene 2.1.8 and 3.0.0b7.
Other function to preserve backwards compatibiolity may be added in the future
"""
import itertools
from typing import Dict, Optional, Callable, Union

from graphene import Schema
from graphene.types.schema import TypeMap


def get_graphene_version(schema: Schema) -> int:
    """
    Main function used to detect which version of graphene we are currently using.

    :param schema: schema that has been generated by graphene
    """
    if hasattr(schema, "_type_map"):
        return 2
    return 3


def perform_graphql_query(schema: Schema, query: str):
    major = get_graphene_version(schema)
    if major == 2:
        from graphql import graphql

        result = graphql(schema, query)
        return result
    elif major == 3:
        from graphql import graphql_sync

        result = graphql_sync(schema.graphql_schema, query)
        return result
    else:
        raise ValueError(f"invalid graphene major version {major}")


def assert_schema_is(actual: Schema, expected_2: str, expected_3: str):
    major = get_graphene_version(actual)
    actual_str = get_schema_str(actual)
    if major == 2:
        assert (
            actual_str == expected_2
        ), f"\n{actual_str}\n!=\n{expected_2}\nDIFFERENCES: {list(filter(lambda x: x[1][0] != x[1][1], enumerate(zip(actual_str.strip(), expected_2.strip()))))}"
    elif major == 3:
        assert (
            actual_str == expected_3
        ), f"\n{actual_str}\n!=\n{expected_3}\nDIFFERENCES: {list(filter(lambda x: x[1][0] != x[1][1], enumerate(zip(actual_str.strip(), expected_3.strip()))))}"
    else:
        assert False, f"invalid major version {major}"


def assert_graphql_response_data(
    schema: Schema, actual: str, expected_2: str, expected_3: str
):
    major = get_graphene_version(schema)
    if major == 2:
        assert (
            actual.strip() == expected_2.strip()
        ), f"\n{actual.strip()}\n!=\n{expected_2.strip()}\nDIFFERENCES: {list(filter(lambda x: x[1][0] != x[1][1], enumerate(zip(actual.strip(), expected_3.strip()))))}"
    elif major == 3:
        assert (
            actual.strip() == expected_3.strip()
        ), f"\n{actual.strip()}\n!=\n{expected_3.strip()}\nDIFFERENCES: {list(filter(lambda x: x[1][0] != x[1][1], enumerate(zip(actual.strip(), expected_3.strip()))))}"
    else:
        raise ValueError(f"invalid graphene major version {major}")


def call_schema_print_fields(schema: Schema, t: type) -> Dict[str, any]:
    major = get_graphene_version(schema)
    if major == 2:
        from graphql.utils.schema_printer import (
            _print_fields as print_fields,
            _print_args,
            _print_deprecated,
        )

        # TODO remove
        # def _print_fields_copy(type: Union["GraphQLObjectType", "GraphQLInterfaceType"]) -> str:
        #     return "\n".join(f"  {f_name}{_print_args(f)}: {f.type}{_print_deprecated(f)}" for f_name, f in type.fields.items())
        # return _print_fields_copy(t)
        return print_fields(t)  # yields ' userId: ID!\n '

    elif major == 3:
        from graphql.utilities.print_schema import (
            print_fields,
            print_description,
            print_args,
            print_deprecated,
        )

        # copy of print_fields from graphene 3.0.0 where we avoid calling print_blocks
        def print_fields_compliant(_type: any):
            fields = [
                print_description(field, "  ", not i)
                + f"  {name}"
                + print_args(field.args, "  ")
                + f": {field.type}"
                + print_deprecated(field.deprecation_reason)
                for i, (name, field) in enumerate(_type.fields.items())
            ]
            return "\n".join(fields)

        return print_fields_compliant(t)
    else:
        raise ValueError(f"invalid graphene major version {major}")


def get_schema_str(schema: Schema) -> str:
    major = get_graphene_version(schema)
    if major == 2:
        return str(schema)
    elif major == 3:
        from graphql.utilities.print_schema import (
            print_schema,
            print_schema_definition,
            print_directive,
            print_type,
            print_introspection_schema,
        )
        from graphql.utilities.print_schema import print_schema_definition

        def print_schema_definition_forced(
            schema: "GraphQLSchema",
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
    else:
        raise ValueError(f"invalid graphene major version {major}")


def get_type_map_from_schema(schema: Schema) -> TypeMap:
    major = get_graphene_version(schema)
    if major == 2:
        return schema._type_map
    elif major == 3:
        return schema.graphql_schema.type_map
    else:
        raise ValueError(f"invalid graphene major version {major}")


def call_schema_get_type(schema: Schema, name: str) -> Optional["GraphQLNamedType"]:
    major = get_graphene_version(schema)
    if major == 2:
        return schema.get_type(name)
    elif major == 3:
        return schema.graphql_schema.get_type(name)
    else:
        raise ValueError(f"invalid graphene major version {major}")


def is_schema_in_auto_camelcase(schema: Schema) -> bool:
    major = get_graphene_version(schema)
    if major == 2:
        return schema.auto_camelcase
    elif major == 3:
        # I don't know a method to detect whether auto_camelcase has been activated in graphene. Generating the default
        # To manage that, I hardcoded the auto_camelcase when creating the schema, since such information is not stored
        # in the datastructures of graphene (AFAIK)
        if hasattr(schema, "auto_camelcase"):
            return schema.auto_camelcase
        else:
            # Otherwise we trat it as the camel case is set
            return True
    else:
        raise ValueError(f"invalid graphene major version {major}")


# def print_fields(type_: Union[GraphQLObjectType, GraphQLInterfaceType]) -> str:
#     try:
#         # graphene 2.1.8
#         import graphql.utils
#         from graphql.utils.schema_printer import _print_fields as print_fields
#         return print_fields(type_)
#     except ImportError:
#         # graphene 3.0.0
#         from graphql.utilities.print_schema import print_fields
#         return print_fields(type_)
