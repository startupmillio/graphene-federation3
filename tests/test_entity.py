import json

import pytest
from graphene import Field, ID, ObjectType, String
from graphql import graphql
from graphql_relay import to_global_id

from graphene_federation3.entity import key
from graphene_federation3.main import build_schema


@pytest.mark.asyncio
async def test_multiple_keys():
    @key("identifier")
    @key("email")
    class User(ObjectType):
        identifier = ID()
        email = String()

        def resolve_identifier(self, info):
            return to_global_id(self.__class__.__name__, json.dumps(self.identifier))

    class Query(ObjectType):
        user = Field(User)

    schema = build_schema(query=Query)
    query = """
    query ($representations: [_Any]) {
      _entities(representations: $representations) {
        ... on User {
          identifier
        }
      }
    }
    """

    result = await graphql(
        schema.graphql_schema,
        query,
        variable_values={
            "representations": [{"__typename": "User", "identifier": "VXNlcjox"}]
        },
    )
    assert not result.errors
    assert result.data == {"_entities": [{"identifier": "VXNlcjox"}]}


@pytest.mark.asyncio
async def test_multiple_types():
    @key("identifier")
    class User(ObjectType):
        identifier = ID()

        def resolve_identifier(self, info):
            return to_global_id(self.__class__.__name__, json.dumps(self.identifier))

    @key("identifier")
    class NotUser(ObjectType):
        identifier = ID()

        def resolve_identifier(self, info):
            return to_global_id(self.__class__.__name__, json.dumps(self.identifier))

    class Query(ObjectType):
        user = Field(User)
        not_user = Field(NotUser)

    schema = build_schema(query=Query)
    query = """
    query ($representations: [_Any]) {
      _entities(representations: $representations) {
        ... on User {
          identifier
        }
        ... on NotUser {
          identifier
        }
      }
    }
    """

    result = await graphql(
        schema.graphql_schema,
        query,
        variable_values={
            "representations": [
                {"__typename": "User", "identifier": "VXNlcjox"},
                {"__typename": "NotUser", "identifier": "Tm90VXNlcjox"},
                {"__typename": "NotUser", "identifier": "Tm90VXNlcjoy"},
                {"__typename": "User", "identifier": "VXNlcjoy"},
            ]
        },
    )
    assert not result.errors
    assert result.data == {
        "_entities": [
            {"identifier": "VXNlcjox"},
            {"identifier": "Tm90VXNlcjox"},
            {"identifier": "Tm90VXNlcjoy"},
            {"identifier": "VXNlcjoy"},
        ]
    }
