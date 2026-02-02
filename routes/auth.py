from fastapi import APIRouter,status,HTTPException,Depends
from utils.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional
from utils.crypto import verify, hash_password
from utils.generate_jwt import create_token

from models.userModel import User

class NewUser(BaseModel):
    username: str
    email: str
    password: str

class loginUser(BaseModel):
    email: str
    password: str


router = APIRouter()

@router.post("/users/add")
def create_new_user(user: NewUser,db: Session = Depends(get_db)):
    try:
        new_user = User(
            username = user.username,
            email = user.email,
            password = hash_password(user.password)
            )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
        
    except IntegrityError as err:
        db.rollback()
        return err
    



@router.post("/users/login")
def login(user: loginUser,db: Session = Depends(get_db)):
    try:
        found = db.query(User).filter(User.email == user.email).first()
        
        if not found:
            raise HTTPException(status_code=404,detail="No User with this email")
        checkPassword = verify(user.password, str(found.password))
        if not checkPassword:
            raise HTTPException(status_code=400,detail="incorrect password")
        
        token = create_token({"email": found.email, "username": found.username})
        
        return token

        
    except IntegrityError as err:
        db.rollback()
        return err
    


# @router.get("/users")
# def get_all_users(db: Session = Depends(get_db))