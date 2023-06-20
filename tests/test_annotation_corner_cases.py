import pytest
from graphene import Field, ID, ObjectType, String
from graphql import graphql

from graphene_federation3.entity import key
from graphene_federation3.extend import extend, external, requires
from graphene_federation3.main import build_schema

SIMILAR_FIELD_SCHEMA_2 = """schema {
  query: Query
}

type ChatMessage {
  id: ID!
  user: ChatUser
}

type ChatUser {
  uid: ID
  identified: ID
  id: ID
  iD: ID
  ID: ID
}

type Query {
  message(id: ID!): ChatMessage
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = ChatUser

type _Service {
  sdl: String
}
"""
SIMILAR_FIELD_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  message(id: ID!): ChatMessage
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type ChatMessage {
  id: ID!
  user: ChatUser
}

type ChatUser {
  uid: ID
  identified: ID
  id: ID
  iD: ID
  ID: ID
}

union _Entity = ChatUser

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""
SIMILAR_FIELD_RESPONSE_2 = """
type ChatMessage {
  id: ID!
  user: ChatUser
}

type ChatQuery {
  message(id: ID!): ChatMessage
}

extend type ChatUser  @key(fields: "id") {
  uid: ID
  identified: ID
  id: ID @external
  iD: ID
  ID: ID
}
"""
SIMILAR_FIELD_RESPONSE_3 = """type ChatQuery {
  message(id: ID!): ChatMessage
}

type ChatMessage {
  id: ID!
  user: ChatUser
}

extend type ChatUser  @key(fields: "id") {
  uid: ID
  identified: ID
  id: ID @external
  iD: ID
  ID: ID
}
"""

CAMELCASE_SCHEMA_2 = """schema {
  query: Query
}

type Camel {
  autoCamel: String
  forcedCamel: String
  aSnake: String
  aCamel: String
}

type Query {
  camel: Camel
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Camel

type _Service {
  sdl: String
}
"""
CAMELCASE_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  camel: Camel
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type Camel {
  autoCamel: String
  forcedCamel: String
  aSnake: String
  aCamel: String
}

union _Entity = Camel

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""
CAMELCASE_RESPONSE_2 = """
extend type Camel  @key(fields: "autoCamel") {
  autoCamel: String @external
  forcedCamel: String @requires(fields: "autoCamel")
  aSnake: String
  aCamel: String
}

type Query {
  camel: Camel
}
"""
CAMELCASE_RESPONSE_3 = """type Query {
  camel: Camel
}

extend type Camel  @key(fields: "autoCamel") {
  autoCamel: String @external
  forcedCamel: String @requires(fields: "autoCamel")
  aSnake: String
  aCamel: String
}
"""

NOAUTOCAMELCASE_SCHEMA_2 = """schema {
  query: Query
}

type Camel {
  auto_camel: String
  forcedCamel: String
  a_snake: String
  aCamel: String
}

type Query {
  camel: Camel
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Camel

type _Service {
  sdl: String
}
"""
NOAUTOCAMELCASE_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  camel: Camel
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type Camel {
  auto_camel: String
  forcedCamel: String
  a_snake: String
  aCamel: String
}

union _Entity = Camel

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""
NOAUTOCAMELCASE_RESPONSE_2 = """
extend type Camel  @key(fields: "auto_camel") {
  auto_camel: String @external
  forcedCamel: String @requires(fields: "auto_camel")
  a_snake: String
  aCamel: String
}

type Query {
  camel: Camel
}
"""
NOAUTOCAMELCASE_RESPONSE_3 = """type Query {
  camel: Camel
}

extend type Camel  @key(fields: "auto_camel") {
  auto_camel: String @external
  forcedCamel: String @requires(fields: "auto_camel")
  a_snake: String
  aCamel: String
}
"""

FILTER_SCHEMA_2 = """schema {
  query: Query
}

type A {
  id: ID
  b(id: ID): B
}

type B {
  id: ID
}

type Query {
  a: A
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = A | B

type _Service {
  sdl: String
}
"""
FILTER_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  a: A
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type A {
  id: ID
  b(id: ID): B
}

type B {
  id: ID
}

union _Entity = A | B

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""
FILTER_RESPONSE_2 = """
extend type A  @key(fields: "id") {
  id: ID @external
  b(id: ID): B
}

type B @key(fields: "id") {
  id: ID
}

type Query {
  a: A
}
"""
FILTER_RESPONSE_3 = """type Query {
  a: A
}

extend type A  @key(fields: "id") {
  id: ID @external
  b(id: ID): B
}

type B @key(fields: "id") {
  id: ID
}
"""

METANAME_SCHEMA_2 = """schema {
  query: Query
}

type Banana {
  id: ID
  b(id: ID): Potato
}

type Potato {
  id: ID
}

type Query {
  a: Banana
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Banana | Potato

type _Service {
  sdl: String
}
"""
METANAME_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  a: Banana
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type Banana {
  id: ID
  b(id: ID): Potato
}

type Potato {
  id: ID
}

union _Entity = Banana | Potato

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""
METANAME_RESPONSE_2 = """
extend type Banana  @key(fields: "id") {
  id: ID @external
  b(id: ID): Potato
}

type Potato @key(fields: "id") {
  id: ID
}

type Query {
  a: Banana
}
"""
METANAME_RESPONSE_3 = """type Query {
  a: Banana
}

extend type Banana  @key(fields: "id") {
  id: ID @external
  b(id: ID): Potato
}

type Potato @key(fields: "id") {
  id: ID
}
"""


@pytest.mark.asyncio
async def test_similar_field_name(assert_schema_is, assert_graphql_response_data):
    """
    Test annotation with fields that have similar names.
    """

    @extend("id")
    class ChatUser(ObjectType):
        uid = ID()
        identified = ID()
        id = external(ID())
        i_d = ID()
        ID = ID()

    class ChatMessage(ObjectType):
        id = ID(required=True)
        user = Field(ChatUser)

    class ChatQuery(ObjectType):
        message = Field(ChatMessage, id=ID(required=True))

    chat_schema = build_schema(query=ChatQuery)
    assert_schema_is(
        actual=chat_schema,
        expected=SIMILAR_FIELD_SCHEMA_3,
    )
    # Check the federation service schema definition language
    query = """
    query {
        _service {
            sdl
        }
    }
    """
    result = await graphql(chat_schema.graphql_schema, query)
    assert not result.errors
    assert_graphql_response_data(
        actual=result.data["_service"]["sdl"].strip(),
        expected=SIMILAR_FIELD_RESPONSE_3,
    )


@pytest.mark.asyncio
async def test_camel_case_field_name(assert_schema_is, assert_graphql_response_data):
    """
    Test annotation with fields that have camel cases or snake case.
    """

    @extend("auto_camel")
    class Camel(ObjectType):
        auto_camel = external(String())
        forcedCamel = requires(String(), fields="auto_camel")
        a_snake = String()
        aCamel = String()

    class Query(ObjectType):
        camel = Field(Camel)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=CAMELCASE_SCHEMA_3,
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
        expected=CAMELCASE_RESPONSE_3,
    )


@pytest.mark.asyncio
async def test_camel_case_field_name_without_auto_camelcase(
    assert_schema_is, assert_graphql_response_data
):
    """
    Test annotation with fields that have camel cases or snake case but with the auto_camelcase disabled.
    """

    @extend("auto_camel")
    class Camel(ObjectType):
        auto_camel = external(String())
        forcedCamel = requires(String(), fields="auto_camel")
        a_snake = String()
        aCamel = String()

    class Query(ObjectType):
        camel = Field(Camel)

    schema = build_schema(query=Query, auto_camelcase=False)
    assert_schema_is(
        actual=schema,
        expected=NOAUTOCAMELCASE_SCHEMA_3,
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
        expected=NOAUTOCAMELCASE_RESPONSE_3,
    )


@pytest.mark.asyncio
async def test_annotated_field_also_used_in_filter(
    assert_schema_is, assert_graphql_response_data
):
    """
    Test that when a field also used in filter needs to get annotated, it really annotates only the field.
    See issue https://github.com/preply/graphene-federation/issues/50
    """

    @key("id")
    class B(ObjectType):
        id = ID()

    @extend("id")
    class A(ObjectType):
        id = external(ID())
        b = Field(B, id=ID())

    class Query(ObjectType):
        a = Field(A)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=FILTER_SCHEMA_3,
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
        expected=FILTER_RESPONSE_3,
    )


async def test_annotate_object_with_meta_name(
    assert_schema_is, assert_graphql_response_data
):
    @key("id")
    class B(ObjectType):
        class Meta:
            name = "Potato"

        id = ID()

    @extend("id")
    class A(ObjectType):
        class Meta:
            name = "Banana"

        id = external(ID())
        b = Field(B, id=ID())

    class Query(ObjectType):
        a = Field(A)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=METANAME_SCHEMA_3,
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
        expected=METANAME_RESPONSE_3,
    )
