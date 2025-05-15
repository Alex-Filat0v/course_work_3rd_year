from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import date
from db.db_module import DataBaseConnector

auth_router = APIRouter()
database = DataBaseConnector()


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
def login(auth: AuthRequest) -> dict:
    user_data = {
        'username': auth.username,
        'password': auth.password
    }
    user = database.user_authorization(user_data)
    if not user:
        raise HTTPException(status_code=401, detail="Ошибка авторизации")
    return {"message": "Авторизация пользователя", "username": user_data["username"]}


@auth_router.post("/registrations")
def login(auth: RegistrationRequest) -> dict:
    user_data = {
        'surname': auth.surname,
        'first_name': auth.first_name,
        'patronymic': auth.patronymic,
        'mail': auth.mail,
        'phone_number': auth.phone_number,
        'birth_date': auth.birth_date,
        'username': auth.username,
        'password': auth.password
    }

    answer_from_db = database.user_registration(user_data)

    if answer_from_db is True:
        return {"error": False, "message": "Пользователь успешно зарегистрирован"}
    else:
        raise HTTPException(status_code=401, detail=f"{answer_from_db}")
