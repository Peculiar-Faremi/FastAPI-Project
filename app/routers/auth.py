from fastapi import APIRouter, HTTPException,status,Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import verify_password
from app import oauth2


router=APIRouter(
    tags=["Authentication"]
    )

@router.post("/login", status_code=status.HTTP_200_OK,response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm= Depends(), db: Session= Depends(get_db)):
    user = db.query (models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    access_token= oauth2.create_access_token(data={"user_id": user.id})
    refresh_token= oauth2.create_refresh_token(data={"user_id": user.id})
    return schemas.Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@router.post("/refresh", status_code=status.HTTP_200_OK,response_model=schemas.Token)
def refresh(refresh_request: schemas.RefreshRequest, db: Session= Depends(get_db)):
    credentials_exceptions=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Credentials could not be validated", headers={"WWW-Authenticate": "Bearer"})
    token= oauth2.verify_refresh_token(refresh_request.refresh_token, credentials_exceptions)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    if user is None:
        raise credentials_exceptions
    access_token= oauth2.create_access_token(data={"user_id": user.id})
    return schemas.Token(access_token=access_token, token_type="bearer", refresh_token=refresh_request.refresh_token)
