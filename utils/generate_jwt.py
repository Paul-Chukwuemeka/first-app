from jose import jwt
from datetime import datetime,timedelta
import os
from dotenv import load_dotenv


load_dotenv()

secret = os.getenv("SECRET") 
algorithm = "HS256"
expire = 60


def create_token(data: dict):
    encoded = data.copy()
    expireTime = datetime.utcnow() + timedelta(minutes = expire)
    encoded.update({"exp": expireTime})
    
    return jwt.encode(encoded,str(secret),algorithm=algorithm)
    
