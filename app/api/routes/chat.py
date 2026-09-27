"""
Chatbot endpoint: ask natural-language questions about the student database.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.chatbot.graph import ask

router = APIRouter(prefix="/chat", tags=["chatbot"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = ask(request.question)
    return ChatResponse(answer=answer)
