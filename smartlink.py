import random, string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database, auth

router = APIRouter()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@router.post("/smartlink/create", response_model=schemas.SmartLinkResponse)
def create_smartlink(data: schemas.SmartLinkCreate, 
                     db: Session = Depends(database.get_db),
                     current_user: models.User = Depends(auth.get_current_user)):
    short_code = generate_short_code()
    db_link = models.SmartLink(original_url=data.original_url, short_code=short_code, user_id=current_user.id)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

@router.get("/smartlink/{short_code}")
def redirect_link(short_code: str, db: Session = Depends(database.get_db)):
    db_link = db.query(models.SmartLink).filter(models.SmartLink.short_code == short_code).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    db_link.clicks += 1
    db.commit()
    return {"original_url": db_link.original_url, "clicks": db_link.clicks}

@router.get("/smartlink/my", response_model=list[schemas.SmartLinkResponse])
def get_my_links(db: Session = Depends(database.get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    links = db.query(models.SmartLink).filter(models.SmartLink.user_id == current_user.id).all()
    return links
