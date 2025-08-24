from pydantic import BaseModel

class ai_suggestions_request(BaseModel):
    product_name:str
    brand:str
    model:str

class ai_suggestions_response(BaseModel):
    description:str
    price:str