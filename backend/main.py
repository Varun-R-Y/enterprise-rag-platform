from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.init_db import init_db
from app.api.auth import router as auth_router
from app.api.document import router as document_router
from app.api.routes.chat import router as chat_router
from app.api.conversation import router as conversation_router

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
app.include_router(document_router)
app.include_router(chat_router)
app.include_router(conversation_router)

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
