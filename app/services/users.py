from app.security import hash_password
from app import models, schemas
from sqlalchemy.orm import Session

def create_user(db: Session, new_user: schemas.CreateUser):
    data = new_user.model_dump()
    data["password"] = hash_password(data["password"])
    user = models.User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user