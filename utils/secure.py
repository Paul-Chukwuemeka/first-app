from fastapi import Depends,HTTPException
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models.userModel import User,roles
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from utils.db import get_db


load_dotenv()

secret = os.getenv("SECRET") 
algorithm = "HS256"

oauth = OAuth2PasswordBearer(tokenUrl="login")


def get_user_by_id(id: UUID,db: Session = Depends(get_db)):
   try:
    found = db.query(User).get(id)
    return found
   except IntegrityError as err:
       return err



def getUser(token = Depends(oauth), db: Session = Depends(get_db)):
    try:
        value = jwt.decode(token,str(secret),algorithms=[algorithm])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    
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