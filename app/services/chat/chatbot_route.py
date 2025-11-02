# app/services/chat/chatbot_route.py
from fastapi import APIRouter, HTTPException, Header
from .chatbot_schema import chat_request, chat_response
from .chatbot import Chat

router = APIRouter(prefix="/api", tags=["Chatbot"])

@router.post("/chatbot", response_model=chat_response)
async def chat_endpoint(request: chat_request, id: str = Header(None)):
    try:
        chat = Chat()
        response = await chat.get_response(request, id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))