from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.init_db import init_db
from app.api.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database tables on application startup
    init_db()
    yield

app = FastAPI(
    title="Enterprise RAG API",
    description="API for Enterprise Retrieval-Augmented Generation (RAG) system",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(auth_router)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Enterprise RAG API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
