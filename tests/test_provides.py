import pytest
from graphene import Field, Int, ObjectType, String
from graphql import graphql

from graphene_federation3.extend import extend, external
from graphene_federation3.main import build_schema
from graphene_federation3.provides import provides

PROVIDES_SCHEMA_2 = """schema {
  query: Query
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Product

type _Service {
  sdl: String
}
"""

PROVIDES_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

union _Entity = Product

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""

PROVIDES_RESPONSE_2 = """
type InStockCount  {
  product: Product! @provides(fields: "name")
  quantity: Int!
}

extend type Product  @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}

type Query {
  inStockCount: InStockCount
}
"""

PROVIDES_RESPONSE_3 = """type Query {
  inStockCount: InStockCount
}

type InStockCount  {
  product: Product! @provides(fields: "name")
  quantity: Int!
}

extend type Product  @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}


"""

MULTIPLE_SCHEMA_2 = """schema {
  query: Query
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Product

type _Service {
  sdl: String
}
"""

MULTIPLE_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

union _Entity = Product

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""

MULTIPLE_RESPONSE_2 = """
type InStockCount  {
  product: Product! @provides(fields: "name weight")
  quantity: Int!
}

extend type Product  @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}

type Query {
  inStockCount: InStockCount
}
"""

MULTIPLE_RESPONSE_3 = """type Query {
  inStockCount: InStockCount
}

type InStockCount  {
  product: Product! @provides(fields: "name weight")
  quantity: Int!
}

extend type Product  @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}
"""

LIST_SCHEMA_2 = """schema {
  query: Query
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

scalar _Any

union _Entity = Product

type _Service {
  sdl: String
}
"""

LIST_SCHEMA_3 = """schema {
  query: Query
}

type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any]): [_Entity]
  _service: _Service
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

union _Entity = Product

\"\"\"Anything\"\"\"
scalar _Any

type _Service {
  sdl: String
}
"""

LIST_RESPONSE_2 = """
type InStockCount  {
  product: Product! @provides(fields: "name weight")
  quantity: Int!
}

extend type Product  @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}

type Query {
  inStockCount: InStockCount
}
"""

LIST_RESPONSE_3 = """type Query {
  inStockCount: InStockCount
}

type InStockCount  {
  product: Product! @provides(fields: "name weight")
  quantity: Int!
}

extend type Product  @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}
"""

SDL_QUERY = """
query {
    _service {
        sdl
    }
}
"""


@pytest.mark.asyncio
async def test_provides(assert_schema_is, assert_graphql_response_data):
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    @provides
    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields="name")
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=PROVIDES_SCHEMA_3,
    )
    # Check the federation service schema definition language
    result = await graphql(schema.graphql_schema, SDL_QUERY)
    assert not result.errors
    assert_graphql_response_data(
        actual=result.data["_service"]["sdl"].strip(),
        expected=PROVIDES_RESPONSE_3,
    )


@pytest.mark.asyncio
async def test_provides_multiple_fields(assert_schema_is, assert_graphql_response_data):
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    @provides
    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields="name weight")
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=MULTIPLE_SCHEMA_3,
    )
    # Check the federation service schema definition language
    result = await graphql(schema.graphql_schema, SDL_QUERY)
    assert not result.errors
    assert_graphql_response_data(
        actual=result.data["_service"]["sdl"].strip(),
        expected=MULTIPLE_RESPONSE_3,
    )


@pytest.mark.asyncio
async def test_provides_multiple_fields_as_list(
    assert_schema_is, assert_graphql_response_data
):
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    @provides
    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields=["name", "weight"])
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query)
    assert_schema_is(
        actual=schema,
        expected=LIST_SCHEMA_3,
    )
    # Check the federation service schema definition language
    result = await graphql(schema.graphql_schema, SDL_QUERY)
    assert not result.errors
    assert_graphql_response_data(
        actual=result.data["_service"]["sdl"].strip(),
        expected=LIST_RESPONSE_3,
    )
