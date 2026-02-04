from fastapi import APIRouter,status,HTTPException,Depends
from utils.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from utils.crypto import verify, hash_password
from utils.generate_jwt import create_token
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from models.userModel import User,roles
import os
from jose import jwt
from enum import Enum



load_dotenv()

secret = os.getenv("SECRET") 
algorithm = "HS256"

class NewUser(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = None

class loginUser(BaseModel):
    email: str
    password: str

    

router = APIRouter()

oauth = OAuth2PasswordBearer(tokenUrl="login")


def getUser(token = Depends(oauth), db: Session = Depends(get_db)):
    value = jwt.decode(token,str(secret),algorithms=[algorithm])
    id = value["id"]
    found = get_user_by_id(id, db)
    if not found or isinstance(found, Exception):
        raise HTTPException(status_code=400,detail="invalid token")
    if (found.token_version != value["token_version"]):
        raise HTTPException(status_code=400,detail="invalid token")
    return found


def verify_roles(*allowed: roles):
    def _verify(user:User = Depends(getUser)):
        if(user.role not in allowed):
            raise HTTPException(status_code=404,detail="Invalid Role")
        return user
    return _verify


@router.post("/users/add")
def create_new_user(user: NewUser,db: Session = Depends(get_db)):
    try:
        new_user = User(
    username=user.username,
    email=user.email,
    password=hash_password(user.password),
    role=roles(user.role) if user.role else roles.customer
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
        found.token_version = found.token_version + 1
        db.commit()
        
        token = create_token({"id": str(found.user_id), "token_version": found.token_version})
        return token

        
    except IntegrityError as err:
        db.rollback()
        return err
    


@router.get('/users/me')
def get_current_user(user = Depends(getUser)):
   return "user"


@router.get("/users/{id}")
def get_user_by_id(id: UUID,db: Session = Depends(get_db)):
   try:
    found = db.query(User).get(id)
    return found
   except IntegrityError as err:
       return err
   

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
   try:
    found = db.query(User).all()
    return found
   except IntegrityError as err:
       return err
   
   
@router.patch("/users/promote/{id}")
def promote_user(id:UUID,db:Session = Depends(get_db),verify = Depends(verify_roles(roles.admin))):
    try:
        found = db.query(User).filter(User.user_id == id).first()
        if not found:
            raise HTTPException(status_code=404,detail="user not found")
        found.role = roles.admin
        db.commit()
        db.refresh(found)
        return found
        
    except IntegrityError as err:
        db.rollback()
        return err