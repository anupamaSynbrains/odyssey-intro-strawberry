from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from strawberry.fastapi import GraphQLRouter
from api.schema import schema
from mock_spotify_rest_api_client.client import Client

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with Client(
        base_url="https://spotify-clone-api-demo.up.railway.app/v1"
    ) as client:
        yield {"spotify_client": client}

# 1. Initialize FastAPI ONCE with the lifespan
app = FastAPI(lifespan=lifespan)

# 2. Add CORS middleware to the app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["https://studio.apollographql.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Define the context getter to pass the Spotify client into your GraphQL resolvers
async def get_context(request: Request):
    spotify_client = request.state.spotify_client
    return {"spotify_client": spotify_client}

# 4. Create the GraphQL router with path="/graphql" and your context getter
graphql_router = GraphQLRouter(
    schema, 
    path="/graphql", 
    graphql_ide="apollo-sandbox", 
    context_getter=get_context
)

# 5. Include the router in your app
app.include_router(graphql_router)