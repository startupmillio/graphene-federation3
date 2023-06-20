import pytest
from graphene import Field, ID, Int, ObjectType, String
from graphql import graphql

from graphene_federation3.extend import extend, external, requires
from graphene_federation3.main import build_schema

PRODUCT_SCHEMA_2 = """schema {
  query: Query
}

type Product {
  sku: ID
  size: Int
  weight: Int
  shippingEstimate: String
}

type Query {
  product: Product
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Product

type _Service {
  sdl: String
}
"""
PRODUCT_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  product: Product
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type Product {
  sku: ID
  size: Int
  weight: Int
  shippingEstimate: String
}

union _Entity = Product

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""

PRODUCTION_RESPONSE_2 = """
extend type Product  @key(fields: "sku") {
  sku: ID @external
  size: Int @external
  weight: Int @external
  shippingEstimate: String @requires(fields: "size weight")
}

type Query {
  product: Product
}
"""

PRODUCTION_RESPONSE_3 = """type Query {
  product: Product
}

extend type Product  @key(fields: "sku") {
  sku: ID @external
  size: Int @external
  weight: Int @external
  shippingEstimate: String @requires(fields: "size weight")
}
"""

MULTIPLE_FIELDS_SCHEMA_2 = """schema {
  query: Query
}

type Product {
  sku: ID
  size: Int
  weight: Int
  shippingEstimate: String
}

type Query {
  product: Product
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Product

type _Service {
  sdl: String
}
"""

MULTIPLE_FIELDS_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  product: Product
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type Product {
  sku: ID
  size: Int
  weight: Int
  shippingEstimate: String
}

union _Entity = Product

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""

MULTIPLE_FIELDS_RESPONSE_2 = """
extend type Product  @key(fields: "sku") {
  sku: ID @external
  size: Int @external
  weight: Int @external
  shippingEstimate: String @requires(fields: "size weight")
}

type Query {
  product: Product
}
"""

MULTIPLE_FIELDS_RESPONSE_3 = """type Query {
  product: Product
}

extend type Product  @key(fields: "sku") {
  sku: ID @external
  size: Int @external
  weight: Int @external
  shippingEstimate: String @requires(fields: "size weight")
}
"""

INPUT_SCHEMA_2 = """schema {
  query: Query
}

type Acme {
  id: ID!
  age: Int
  foo(someInput: String): String
}

type Query {
  acme: Acme
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Acme

type _Service {
  sdl: String
}
"""

INPUT_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  acme: Acme
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type Acme {
  id: ID!
  age: Int
  foo(someInput: String): String
}

union _Entity = Acme

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""

INPUT_RESPONSE_2 = """
extend type Acme  @key(fields: "id") {
  id: ID! @external
  age: Int @external
  foo(someInput: String): String @requires(fields: "age")
}

type Query {
  acme: Acme
}
"""

INPUT_RESPONSE_3 = """type Query {
  acme: Acme
}

extend type Acme  @key(fields: "id") {
  id: ID! @external
  age: Int @external
  foo(someInput: String): String @requires(fields: "age")
}
"""


def test_chain_requires_failure():
    """
    Check that we can't nest call the requires method on a field.
    """
    with pytest.raises(AssertionError) as err:

        @extend("id")
        class A(ObjectType):
            id = external(ID())
            something = requires(requires(String(), fields="id"), fields="id")

    assert "Can't chain `requires()` method calls on one field." == str(err.value)


@pytest.mark.asyncio
async def test_requires_multiple_fields(assert_schema_is, assert_graphql_response_data):
    """
    Check that requires can take more than one field as input.
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(ID())
        size = external(Int())
        weight = external(Int())
        shipping_estimate = requires(String(), fields="size weight")

    class Query(ObjectType):
        product = Field(Product)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=PRODUCT_SCHEMA_3,
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
        expected=PRODUCTION_RESPONSE_3,
    )


async def test_requires_multiple_fields_as_list(
    assert_schema_is, assert_graphql_response_data
):
    """
    Check that requires can take more than one field as input.
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(ID())
        size = external(Int())
        weight = external(Int())
        shipping_estimate = requires(String(), fields=["size", "weight"])

    class Query(ObjectType):
        product = Field(Product)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=MULTIPLE_FIELDS_SCHEMA_3,
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
        expected=MULTIPLE_FIELDS_RESPONSE_3,
    )


@pytest.mark.asyncio
async def test_requires_with_input(assert_schema_is, assert_graphql_response_data):
    """
    Test checking that the issue https://github.com/preply/graphene-federation/pull/47 is resolved.
    """

    @extend("id")
    class Acme(ObjectType):
        id = external(ID(required=True))
        age = external(Int())
        foo = requires(Field(String, someInput=String()), fields="age")

    class Query(ObjectType):
        acme = Field(Acme)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=INPUT_SCHEMA_3,
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
        expected=INPUT_RESPONSE_3,
    )
