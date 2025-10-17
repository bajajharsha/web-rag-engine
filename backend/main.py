from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.database import mongodb_database
from backend.routes import url_route


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    mongodb_database.connect()

    yield

    mongodb_database.disconnect()


app = FastAPI(title="Web RAG Engine", lifespan=db_lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(url_route.router, prefix="/api/v1", tags=["URL"])


@app.get("/")
async def root():
    return {"message": "Welcome to Web RAG Engine API!"}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
