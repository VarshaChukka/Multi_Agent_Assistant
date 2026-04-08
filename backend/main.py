import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.orchestrator import Orchestrator
from database.db import init_db
from models.schemas import ChatRequest, ChatResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("api")

app = FastAPI(
    title="Multi-Agent Assistant",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

# Single chat endpoint that returns combined agent responses.


@app.on_event("startup")
def setup_database() -> None:
    init_db()


@app.get("/")
def root() -> dict:
    return {"message": "API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("Received chat message")
    response_text = orchestrator.handle_message(request.message)
    return ChatResponse(response=response_text)
