from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from app.menu.models import SizeEnum

class VariantCreate(BaseModel):
    size :  SizeEnum
    price: Decimal

class VariantResponse(BaseModel):
    id : int
    size : SizeEnum
    price : Decimal
    class Config:
        from_attributes  = True

class MenuItemCreate(BaseModel):
    restaurant_id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    variants: List[VariantCreate]

class MenuItemResponse(BaseModel):
    id : int
    restaurant_id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    image_url: Optional[str]
    is_available: bool
    variants: List[VariantResponse]

    class Config:
        from_attributes = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None