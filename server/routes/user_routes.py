from fastapi import APIRouter, HTTPException, Query
from typing import List
from pydantic import BaseModel
from server.database.db_module import db_connector


user_router = APIRouter()


class UserOut(BaseModel):
    username: str
    first_name: str
    surname: str


@user_router.get("/users/search", response_model=List[UserOut])
async def search_for_users(current_user: str, query: str = Query(..., min_length=2)):
    if not query:
        return []
    users = await db_connector.search_users(query, current_user)
    return users


@user_router.get("/contacts/{username}", response_model=List[UserOut])
async def get_user_contacts(username: str):
    contacts = await db_connector.get_contacts(username)
    return contacts


@user_router.post("/contacts/{owner_username}/add/{contact_username}", status_code=201)
async def add_user_to_contacts(owner_username: str, contact_username: str):
    if owner_username == contact_username:
        raise HTTPException(status_code=400, detail="Cannot add yourself to contacts")

    success = await db_connector.add_contact(owner_username, contact_username)
    if not success:
        raise HTTPException(status_code=400, detail="Contact already exists")
    return {"message": "Contact added successfully"}
