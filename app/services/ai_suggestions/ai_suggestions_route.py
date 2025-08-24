from fastapi import APIRouter, HTTPException
from .ai_suggestions_schema import ai_suggestions_request, ai_suggestions_response
from .ai_suggestions import Suggestion

router = APIRouter(prefix="/api", tags=["AI Suggestions"])

@router.post("/ai_suggestions", response_model=ai_suggestions_response)
async def ai_suggestions(request: ai_suggestions_request):
    try:
        suggestion = Suggestion()
        response = suggestion.get_suggestion(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))