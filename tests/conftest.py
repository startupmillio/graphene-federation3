from unittest.mock import patch

import pytest
from graphene import Schema
from graphql import ASTValidationRule, GraphQLError

from graphene_federation3.graphql_compatibility import get_schema_str


@pytest.fixture
def raise_graphql():
    def r(self, x, *args, **kwargs):
        raise x

    def init(
        self,
        message: str,
        nodes=None,
        source=None,
        positions=None,
        path=None,
        original_error=None,
        extensions=None,
    ):
        if isinstance(original_error, Exception):
            raise original_error
        else:
            raise Exception(message)

    with patch.object(ASTValidationRule, "report_error", r), patch.object(
        GraphQLError, "__init__", init
    ):
        yield


@pytest.fixture
def assert_schema_is():
    def cmp(actual: Schema, expected: str):
        assert get_schema_str(actual).strip() == expected.strip()

    return cmp


@pytest.fixture
def assert_graphql_response_data():
    def cmp(actual: str, expected: str):
        assert actual.strip() == expected.strip()

    return cmp
