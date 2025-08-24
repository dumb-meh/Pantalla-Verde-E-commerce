from pydantic import BaseModel

class chat_request(BaseModel):
    message:str

class chat_response(BaseModel):
    respopnse:str