from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db
from app.services import products as product_service
from app.oauth2 import get_current_user
from app.schemas import Product, ProductResponse
import json
from app.redis_client import r

router = APIRouter(prefix="/products", tags=["Products"])

def clear_user_cache(current_user: models.User = Depends(oauth2.get_current_user)):
    # Products changed, so delete this user's saved lists
    for key in r.scan_iter(f"products:user:{current_user.id}:*"):
        r.delete(key)

@router.post("/post", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(clear_user_cache)])
def create_product(
    new_product: schemas.Product, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
): 
    return product_service.create_product(db, new_product, current_user.id)

@router.get("/get/{id}",response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    cache_key = f"products:user:{current_user.id}:id:{id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    product = product_service.get_product(db, id, current_user.id)
    data = ProductResponse.model_validate(product).model_dump(mode="json")
    # Save for 60 seconds, then Redis deletes it
    r.set(cache_key, json.dumps(data), ex=60)
    return data

@router.get("/getall", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_all_products(db: Session = Depends(get_db),
                        current_user=Depends(oauth2.get_current_user),
                        skip:int=Query(0, le=100, ge=0), #default skip is 0, max limit is 100, min limit is 0
                        limit:int=Query(10, le=100, ge=1), #default limit is 10, max limit is 100, min limit is 1
                        search: Optional[str] = Query(None)): #liberty to search for keywords in the product name or description.
    cache_key = f"products:user:{current_user.id}:skip:{skip}:limit:{limit}:search:{search}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    products = product_service.get_all_products(
        db, current_user.id, skip=skip, limit=limit, search=search
    )
    data = [ProductResponse.model_validate(p).model_dump(mode="json") for p in products]
    # Save for 60 seconds, then Redis deletes it
    r.set(cache_key, json.dumps(data), ex=60,  )
    return data

@router.put("/update/{id}", response_model=ProductResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(clear_user_cache)])
def update_product(id: int, updated_product: Product, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    return product_service.update_product(db, id, updated_product, current_user.id)

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(clear_user_cache)])
def delete_product(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):    
    return product_service.delete_product(db, id, current_user.id)

@router.post("/order/{product_id}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(clear_user_cache)])
def order_product(
    product_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
): 
    return product_service.order_product(db, product_id, current_user.id)