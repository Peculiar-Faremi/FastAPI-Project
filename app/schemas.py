from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
class Details(BaseModel):
    description:str
    review:Optional[str] = None

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    created_at:datetime

    model_config = {"from_attributes": True}

class Product(BaseModel):
    name:str
    price:int
    details:Details

    @field_validator("name")
    @classmethod
    def name_contains_alphabet(cls, n:str):
        if not n.replace(" ", "").isalnum():
            raise ValueError("Name must contain only numbers and letters")
        return n.title()
    
class ProductResponse(BaseModel):
        id:int
        is_ordered:bool
        ordered_at: Optional[datetime] = None
        created_at: datetime
        name:str
        details:Details
        price:int

        owner:UserResponse

        model_config = {"from_attributes": True}

class CreateUser(BaseModel):
    email:EmailStr
    password:str

class UserLogin(BaseModel):
     email:EmailStr
     password:str

class TokenData(BaseModel):
     id:int

class RefreshRequest(BaseModel):
    refresh_token:str