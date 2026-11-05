from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total: float

class OrderCreate(BaseModel):
    full_name: str
    phone: str
    address: str
    city: str
    postal_code: str

class OrderItemResponse(BaseModel):
    id: int
    product_id: int | None = None
    product_name: str
    price: float
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    total: float
    status: str
    full_name: str
    phone: str
    address: str
    city: str
    postal_code: str
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    question: str

class ChatSource(BaseModel):
    manual: str
    section: str
    download_link: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = []
