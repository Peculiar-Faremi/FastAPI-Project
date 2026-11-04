from jose import jwt,JWTError
from app import schemas,database, models
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings

SECRET_KEY= settings.SECRET_KEY
ALGORITHM= settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES= settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS= settings.REFRESH_TOKEN_EXPIRE_DAYS

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="login") #reads the Beraer token from the request header and passes it to the get_current_user function

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc) + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire, "type":"access"})
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token:str, credentials_exceptions):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exceptions
        id = payload.get("user_id")
        if id is None:
            raise credentials_exceptions
        token_data= schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exceptions
    return token_data

def get_current_user(token:str= Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exceptions=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credentials could not be validated", 
                                         headers={"WWW-Authenticate": "Bearer"})
    token= verify_access_token(token, credentials_exceptions)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    if user is None:
        raise credentials_exceptions
    return user

def create_refresh_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc) + timedelta(days= settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp":expire, "type":"refresh"}) #marks this token as a refresh token
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token:str, credentials_exceptions):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh": #from line 49, this token is not a refresh token and throws an error
            raise credentials_exceptions
        id = payload.get("user_id")
        if id is None:
            raise credentials_exceptions
        token_data= schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exceptions
    return token_data

