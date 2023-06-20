import pytest
from graphene import Field, ID, ObjectType, String
from graphql import graphql

from graphene_federation3.entity import key
from graphene_federation3.main import build_schema

MULTIPLE_KEYS_SCHEMA_2 = """schema {
  query: Query
}

type Query {
  user: User
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type User {
  identifier: ID
  email: String
}

scalar _Any

union _Entity = User

type _Service {
  sdl: String
}
"""
MULTIPLE_KEYS_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  user: User
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type User {
  identifier: ID
  email: String
}

union _Entity = User

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""

MULTIPLE_KEYS_RESPONSE_2 = """
type Query {
  user: User
}

type User @key(fields: "email") @key(fields: "identifier") {
  identifier: ID
  email: String
}
"""

MULTIPLE_KEYS_RESPONSE_3 = """
type Query {
  user: User
}

type User @key(fields: "email") @key(fields: "identifier") {
  identifier: ID
  email: String
}
"""


@pytest.mark.asyncio
async def test_multiple_keys(assert_schema_is, assert_graphql_response_data):
    @key("identifier")
    @key("email")
    class User(ObjectType):
        identifier = ID()
        email = String()

    class Query(ObjectType):
        user = Field(User)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=MULTIPLE_KEYS_SCHEMA_3,
    )
    # Check the federation service schema definition language
    query = """
    query {
        _service {
            sdl
        }
    }
    """
    result = await graphql(schema.graphql_schema, query)
    assert not result.errors
    assert_graphql_response_data(
        actual=result.data["_service"]["sdl"].strip(),
        expected=MULTIPLE_KEYS_RESPONSE_3,
    )


def test_key_non_existing_field_failure():
    """
    Test that using the key decorator and providing a field that does not exist fails.
    """
    with pytest.raises(AssertionError) as err:

        @key("potato")
        class A(ObjectType):
            id = ID()

    assert 'Field "potato" does not exist on type "A"' == str(err.value)


def test_compound_primary_keys_failure():
    """
    Compound primary keys are not implemented as of now so this test checks that at least the user get
    an explicit failure.
    """

    class Organization(ObjectType):
        id = ID()

    with pytest.raises(NotImplementedError) as err:

        @key("id organization { id }")
        class User(ObjectType):
            id = ID()
            organization = Field(Organization)

    assert "Compound primary keys are not supported." == str(err.value)
