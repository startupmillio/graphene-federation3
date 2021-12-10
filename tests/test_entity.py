import json

from graphene import Field, ID, ObjectType, String
from graphql import graphql_sync
from graphql_relay import to_global_id

from graphene_federation3.entity import key
from graphene_federation3.main import build_schema


def test_multiple_keys():
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

    result = graphql_sync(
        schema.graphql_schema,
        query,
        variable_values={
            "representations": [{"__typename": "User", "identifier": "VXNlcjox"}]
        },
    )
    assert not result.errors
    assert result.data == {"_entities": [{"identifier": "VXNlcjox"}]}
