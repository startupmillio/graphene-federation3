import graphene


class _Any(graphene.Scalar):
    """Anything"""

    __typename = graphene.String(required=True)

    @staticmethod
    def serialize(dt):
        return dt

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value
