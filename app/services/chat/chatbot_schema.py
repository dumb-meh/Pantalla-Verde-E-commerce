from pydantic import BaseModel
from typing import List, Optional
class HistoryItem(BaseModel):
    message: str
    response: str
class chat_request(BaseModel):
    message: str
    history: Optional[List[HistoryItem]] = None 
class chat_response(BaseModel):
    response: str
    user_message:str 
    