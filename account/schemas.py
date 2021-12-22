from typing import Optional

from ninja import Schema
from pydantic import EmailStr, Field


class AccountCreate(Schema):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str]
    password1: str = Field(min_length=8)
    Governorate:str
    city:str
    closest_point:str




class AccountOut(Schema):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str]
    Governorate: str = None
    city: str = None
    closest_point: str = None


class TokenOut(Schema):
    access: str

class AuthOut(Schema):
    token: TokenOut
    account: AccountOut

class SigninSchema(Schema):
    email: EmailStr
    password: str


class AccountUpdate(Schema):
    first_name: str
    last_name: str
    phone_number: Optional[str]
    Governorate: str
    city: str
    closest_point: str



class ChangePasswordSchema(Schema):
    old_password: str
    new_password1: str
    new_password2: str
