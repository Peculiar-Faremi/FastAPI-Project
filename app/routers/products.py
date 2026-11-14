from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db
from app.services import products as product_service
from app.oauth2 import get_current_user
from app.schemas import Product, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/post", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    new_product: schemas.Product, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return product_service.create_product(db, new_product, current_user.id)

@router.get("/get/{id}",response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    return product_service.get_product(db, id, current_user.id)

@router.get("/getall", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_all_products(db: Session = Depends(get_db),
                        current_user=Depends(oauth2.get_current_user),
                        skip:int=Query(0, le=100, ge=0), #default skip is 0, max limit is 100, min limit is 0
                        limit:int=Query(10, le=100, ge=1), #default limit is 10, max limit is 100, min limit is 1
                        search: Optional[str] = Query(None)): #liberty to search for keywords in the product name or description.
    return product_service.get_all_products(db, current_user.id, skip=skip, limit=limit, search=search)

@router.put("/update/{id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(id: int, updated_product: Product, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    return product_service.update_product(db, id, updated_product, current_user.id)

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):    
    return product_service.delete_product(db, id, current_user.id)

@router.post("/order/{product_id}", status_code=status.HTTP_201_CREATED)
def order_product(
    product_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
): 
    return product_service.order_product(db, product_id, current_user.id)