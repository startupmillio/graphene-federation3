import graphene
import pytest
from graphene import Connection, Context, ObjectType, String, relay
from graphql import graphql
from graphql_relay import to_global_id

from graphene_federation3.entity import key
from graphene_federation3.main import build_schema

_query = """
query ($representations: [_Any]) {
  _entities(representations: $representations) {
    ... on User {
      id
      email
    }
  }
}
"""


@pytest.mark.asyncio
async def test_global_id(raise_graphql):
    @key("id")
    @key("email")
    class User(ObjectType):
        email = String()

        class Meta:
            interfaces = (relay.Node,)

        @classmethod
        def _resolve_reference_bulk(cls, model, info):
            for field in info.parent_type.fields.values():
                if hasattr(field.type, "name"):
                    field_type_name = field.type.name
                    if (
                        field_type_name.endswith("Connection")
                        and field_type_name[:-10] == info.context.representation
                    ):
                        return field.resolve(model, info)

        @classmethod
        def get_node(cls, info, id):
            return User(id=id, email=f"{id}@email.com")

    class UserConnection(Connection):
        class Meta:
            node = User

        class Edge:
            other = String()

    class Query(ObjectType):
        node = relay.Node.Field()
        users = relay.ConnectionField(UserConnection)

        def resolve_users(root, info):
            return [User.get_node(info, id="identifier")]

    schema = build_schema(query=Query)

    result = await graphql(
        schema.graphql_schema,
        _query,
        variable_values={
            "representations": [{"__typename": "User", "id": "VXNlcjppZGVudGlmaWVy"}]
        },
        context_value=Context,
    )
    assert not result.errors
    assert result.data == {
        "_entities": [{"email": "identifier@email.com", "id": "VXNlcjppZGVudGlmaWVy"}]
    }


@pytest.mark.asyncio
async def test_local_id(raise_graphql):
    @key("id")
    @key("email")
    class User(ObjectType):
        id = graphene.ID(required=True)
        email = String()

        class Meta:
            interfaces = (relay.Node,)

        def resolve_id(self, info):
            return to_global_id(self.__class__.__name__, self.id)

        @classmethod
        def _resolve_reference_bulk(cls, model, info):
            for field in info.parent_type.fields.values():
                if hasattr(field.type, "name"):
                    field_type_name = field.type.name
                    if (
                        field_type_name.endswith("Connection")
                        and field_type_name[:-10] == info.context.representation
                    ):
                        return field.resolve(model, info)

        @classmethod
        def get_node(cls, info, id):
            return User(id=id, email=f"{id}@email.com")

    class UserConnection(Connection):
        class Meta:
            node = User

        class Edge:
            other = String()

    class Query(ObjectType):
        node = relay.Node.Field()
        users = relay.ConnectionField(UserConnection)

        def resolve_users(root, info):
            return [User.get_node(info, id="identifier")]

    schema = build_schema(query=Query)

    result = await graphql(
        schema.graphql_schema,
        _query,
        variable_values={
            "representations": [{"__typename": "User", "id": "VXNlcjppZGVudGlmaWVy"}]
        },
        context_value=Context,
    )
    assert not result.errors
    assert result.data == {
        "_entities": [{"email": "identifier@email.com", "id": "VXNlcjppZGVudGlmaWVy"}]
    }


@pytest.mark.asyncio
async def test_second_key(raise_graphql):
    @key("id")
    @key("email")
    class User(ObjectType):
        email = String()

        class Meta:
            interfaces = (relay.Node,)

        @classmethod
        def _resolve_reference_bulk(cls, model, info):
            for field in info.parent_type.fields.values():
                if hasattr(field.type, "name"):
                    field_type_name = field.type.name
                    if (
                        field_type_name.endswith("Connection")
                        and field_type_name[:-10] == info.context.representation
                    ):
                        return field.resolve(model, info)

        @classmethod
        def get_node(cls, info, id):
            return User(id=id, email=f"{id}@email.com")

    class UserConnection(Connection):
        class Meta:
            node = User

        class Edge:
            other = String()

    class Query(ObjectType):
        node = relay.Node.Field()
        users = relay.ConnectionField(UserConnection)

        def resolve_users(root, info):
            return [User.get_node(info, id="identifier")]

    schema = build_schema(query=Query)

    result = await graphql(
        schema.graphql_schema,
        _query,
        variable_values={
            "representations": [{"__typename": "User", "email": "identifier@email.com"}]
        },
        context_value=Context,
    )
    assert not result.errors
    assert result.data == {
        "_entities": [{"email": "identifier@email.com", "id": "VXNlcjppZGVudGlmaWVy"}]
    }
