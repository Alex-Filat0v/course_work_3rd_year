from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import date
from server.database.db_module import db_connector

auth_router = APIRouter()


class AuthRequest(BaseModel):
    username: str
    password: str


class RegistrationRequest(BaseModel):
    surname: str
    first_name: str
    patronymic: str
    mail: EmailStr
    phone_number: PhoneNumber
    birth_date: date
    username: str
    password: str


@auth_router.post("/auth")
async def login(auth: AuthRequest) -> dict:
    user_authorized = await db_connector.user_authorization(auth.dict())
    if not user_authorized:
        raise HTTPException(status_code=401, detail="Ошибка авторизации: неверный логин или пароль")
    return {"message": "Авторизация пользователя", "username": auth.username}


@auth_router.post("/registrations")
async def registration(auth: RegistrationRequest) -> dict:
    user_data = auth.dict()

    user_data['phone_number'] = str(user_data['phone_number'])

    answer_from_db = await db_connector.user_registration(user_data)

    if answer_from_db is True:
        return {"error": False, "message": "Пользователь успешно зарегистрирован"}
    else:
        raise HTTPException(status_code=400, detail=f"Ошибка регистрации: {answer_from_db}")
