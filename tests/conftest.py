from unittest.mock import patch

import pytest
from graphql import ASTValidationRule, GraphQLError


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
