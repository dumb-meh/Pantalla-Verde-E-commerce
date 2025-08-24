from fastapi import APIRouter,HTTPException
from .chatbot_schema import chat_request, chat_response
from .chatbot_schema import Chat

router = APIRouter()
chat= Chat()

@router.post("/chatbot", response_model=chat_response)
async def chat(request: chat_request):
    try:
        response=Chat.get_suggestion(request=chat_request)
        return chat_response (response=response)
    
    except Exception as e:
        raise HTTPException (status_code=500, detail=str(e))
