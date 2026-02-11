from fastapi import APIRouter,status,HTTPException,Depends
from utils.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from utils.crypto import verify, hash_password
from utils.generate_jwt import create_token
from models.userModel import User,roles
from utils.secure import getUser, verify_roles
import random
from datetime import datetime, timedelta,timezone

class NewUser(BaseModel):
    username: str
    email: str
    password: str

class loginUser(BaseModel):
    email: str
    password: str

router = APIRouter()

class otpConfirm(BaseModel):
    otp: int

class UserOut(BaseModel):
    user_id : UUID
    otp : int
    role : str
     
    class Config:
        orm_mode = True

@router.post("/users/add")
def create_new_user(user: NewUser,db: Session = Depends(get_db)):
    try:
        new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role= roles.customer
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
   
@router.patch("/users/upgrade/request", response_model= UserOut)
def upgrade_user(db:Session = Depends(get_db),user = Depends(verify_roles(roles.customer))):
    try:
        otp = random.randint(1000,9999)
        user.otp = otp
        user.otp_expiry_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        db.commit()
        db.refresh(user)
        return user
    
    
    except IntegrityError as err:
        db.rollback()
        return err
    
@router.post("/users/upgrade/confirm" , response_model= UserOut)
def upgrade_user_confirm(payload:otpConfirm,db:Session = Depends(get_db),user = Depends(verify_roles(roles.customer))):
    try:
        if not user.otp or  user.otp != payload.otp:
            raise HTTPException(status_code=400,detail="invalid otp")
        if user.otp_expiry_time < datetime.now(timezone.utc):
            raise HTTPException(status_code=400,detail="expired otp")
        
        user.role = roles.vendor
        user.otp = None
        user.otp_expiry_time = None
        
        db.commit()
        db.refresh(user)
        return user       
    except IntegrityError as err:
        db.rollback()
        return err


   
#    request --> create otp --> user --> send back --> verify otp --> upgrade the user
   
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