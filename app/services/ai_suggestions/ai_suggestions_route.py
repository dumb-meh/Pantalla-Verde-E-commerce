from fastapi import APIRouter,HTTPException
from .ai_suggestions_schema import ai_suggestions_request, ai_suggestions_response
from .ai_suggestions import Suggestion

router = APIRouter()
suggestion=Suggestion()

@router.post("/ai_suggestions", response_model=ai_suggestions_response)
async def ai_suggestions(request: ai_suggestions_request):
    try:
        response=Suggestion.get_suggestion(request=ai_suggestions_request)
        return ai_suggestions_response (response=response)
    
    except Exception as e:
        raise HTTPException (status_code=500, detail=str(e))
