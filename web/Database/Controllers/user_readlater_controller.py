from sqlalchemy.orm import Session
from Database.Model.models import UserReadLater


def update_user_readlater(db: Session, user_id: int, book_id: int) -> dict:
    # Similar logic to update_user_favorite but for read later functionality
    existing_entry = db.query(UserReadLater).filter(
        UserReadLater.user_id == user_id,
        UserReadLater.book_id == book_id
    ).first()
    status = {"god": "ok"}
    
    if existing_entry:
        if existing_entry.is_readlater:
            existing_entry.is_readlater = False
        else:
            existing_entry.is_readlater = True
        db.commit()
    else:
        new_entry = UserReadLater(user_id=user_id, book_id=book_id, is_readlater=True)
        db.add(new_entry)
        db.commit()
    return status