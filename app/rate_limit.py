from fastapi import HTTPException, status, Depends, Request
from app.redis_client import r
from app import models, oauth2

def limit_requests(current_user: models.User = Depends(oauth2.get_current_user)):
    # Make a unique key for this user
    redis_key = f"rate_limit:user:{current_user.id}"
    
    # Tell Redis to add +1 to their count
    # (If it's their first time, Redis starts the count at 1)
    request_count = r.incr(redis_key)
    
    # If this is their FIRST request, set a timer to reset the count after 60 seconds
    if request_count == 1:
        r.expire(redis_key, 60)
        
    # If they made more than 5 requests, block them!
    if request_count > 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests."
        )
  

def limit_login_by_ip(request: Request):
    # Get the IP address of the person making the request
    client_ip = request.client.host
    
    # Create a unique Redis key for this IP address (e.g., "rate_limit:login_ip:127.0.0.1")
    redis_key = f"rate_limit:login_ip:{client_ip}"
    
    request_count = r.incr(redis_key)
     
    if request_count == 1:
        r.expire(redis_key, 60)
        
    if request_count > 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts from this IP. Try again in 60 seconds."
        )