from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from schema import schema
import uvicorn as uvicorn

app = FastAPI()

app.add_route("/graphql", GraphQLApp(schema=schema))

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info",
        reload=False,
    )
