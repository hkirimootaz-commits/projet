from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class ClientCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    prenom: str = Field(min_length=1, max_length=100)
    adresse: str
    telephone: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginData(BaseModel):
    email: EmailStr
    password: str


class ProductCreate(BaseModel):
    nom: str
    description: str = ""
    prix: float = Field(ge=0)
    categorie: Literal["cafe", "food"]
    image_url: str = ""
    disponible: bool = True


class OrderItemInput(BaseModel):
    product_id: int = Field(gt=0)
    quantite: int = Field(gt=0, le=100)


class OrderCreate(BaseModel):
    client_id: int = Field(gt=0)
    items: list[OrderItemInput] = Field(min_length=1)