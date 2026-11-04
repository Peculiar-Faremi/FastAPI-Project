from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, timezone
def build_product(product: models.Product): #USING THIS because we have nested details in the schema, so we need to build the response manually
    return {
        "id": product.id,
        "name": product.name,
        "details": {
            "description": product.description,
            "inventory": product.inventory,
            "review": product.review,
        },
        "price": product.price,
        "ordered_at": product.ordered_at,
        "is_ordered":product.is_ordered,
        "created_at": product.created_at,
        "owner":product.owner
        }


def create_product(db: Session, new_product: schemas.Product, user_id:int):
    data = new_product.model_dump()
    details = data.pop("details")
    data["user_id"] = user_id
    created_product = models.Product(**data, **details)
    
    db.add(created_product)
    db.commit()
    db.refresh(created_product)
    return build_product(created_product)


def get_product(db: Session, id: int, user_id:int):
    product = db.query(models.Product).filter(models.Product.id == id,
                                              models.Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return build_product(product)


def get_all_products(db: Session, user_id:int, skip: int=0, limit: int=10, search: Optional[str] = None): #using skip and limit for pagination
    query=db.query(models.Product).filter(models.Product.user_id == user_id)
    if search:
        query=query.filter(models.Product.name.ilike(f"%{search}%") #searching for keywords in the product name or description using ilike for case-insensitive search
                           | models.Product.description.ilike(f"%{search}%"))
    products = query.offset(skip).limit(limit).all() #applied pagination using offset and limit in the query
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    return [build_product(p) for p in products] 



def update_product(db: Session, id: int, updated_product: schemas.Product, user_id:int):
    product = db.query(models.Product).filter(models.Product.id == id,
                                              models.Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    data = updated_product.model_dump()
    details = data.pop("details")
    for key, value in {**data, **details}.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return build_product(product)

def delete_product(db: Session, id: int, user_id:int):
    product = db.query(models.Product).filter(models.Product.id == id,
                                              models.Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

def order_product(db: Session, product_id: int, user_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if product.is_ordered:
        raise HTTPException(status_code=400, detail="Product is already ordered")
    product.is_ordered = True
    product.ordered_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(product)
    return {"message": "Order placed successfully", "ordered_at": product.ordered_at}