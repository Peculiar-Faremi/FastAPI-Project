from fastapi import APIRouter, HTTPException,status,Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import verify_password
from app import oauth2
from app.rate_limit import limit_login_by_ip 
from app.redis_client import r


router=APIRouter(
    tags=["Authentication"]
    )

# Add the IP bouncer to the route decorator
@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.Token, dependencies=[Depends(limit_login_by_ip)])
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # Find the user by email
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    # CREATE THE EMAIL FAIL KEY BEFORE WE CHECK THE PASSWORD
    # This tracks failures specifically for this email address
    fail_key = f"rate_limit:login_fail:{user_credentials.username}"
    
    # Check if user exists AND if password is correct
    # If the user doesn't exist OR the password is wrong will go inside this block
    if not user or not verify_password(user_credentials.password, user.password):
        fails = r.incr(fail_key)
        # If this is their first fail, set a 5-minute (300 seconds) lockout timer
        if fails == 1:
            r.expire(fail_key, 300)
        # If they have failed 5 or more times, block them
        if fails >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts for this account. Try again in 5 minutes."
            )  
        # If they haven't reached 5 fails yet, just give the normal error
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    # Delete their fail counter so they start with a clean slate next time
    r.delete(fail_key)
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})
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
