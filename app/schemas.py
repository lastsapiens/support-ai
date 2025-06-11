from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --------- User Schemas ---------

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True

# Optional: if used anywhere
class User(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True

# --------- Auth Token Schema ---------

class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    sub: str  # or Optional[str] = None, if it can be missing
    
# --------- Ticket Schemas ---------

class TicketBase(BaseModel):
    title: str
    description: str

class TicketCreate(TicketBase):
    priority: Optional[str] = "medium"
    category: Optional[str] = None
    wing: Optional[str] = None
    section: Optional[str] = None
    attachment_url: Optional[str] = None

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None

class Ticket(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: Optional[str] = None
    category: Optional[str] = None
    wing: Optional[str] = None
    section: Optional[str] = None
    attachment_url: Optional[str] = None
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        orm_mode = True
