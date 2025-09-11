from typing import List, Optional, Union
from pydantic import BaseModel

class ProductKnowledge(BaseModel):
    productId:str
    productName: str
    model: Optional[str] = None
    brand: Optional[str] = None
    type: Optional[str] = None
    color: Union[List[str], str]
    status: Optional[str] = None
    price: Optional[float] = None
    priceWithInstallation: Optional[float] = None
    condition: Optional[str] = None
    warrantyType: Optional[str] = None
    description: Optional[str] = None