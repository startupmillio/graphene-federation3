import uvicorn as uvicorn
from fastapi import FastAPI
from starlette_graphene3 import (
    GraphQLApp,
    make_graphiql_handler,
)

from schema import schema

app = FastAPI()

app.add_route("/graphql", GraphQLApp(schema=schema, on_get=make_graphiql_handler()))

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info",
        reload=False,
    )
