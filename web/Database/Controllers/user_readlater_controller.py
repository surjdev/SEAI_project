from sqlalchemy.orm import Session, joinedload
from Database.Model.models import UserReadLater, Book

def update_user_readlater(db: Session, user_id: int, book_id: int) -> dict:
    # Similar logic to update_user_favorite but for read later functionality
    existing_entry = db.query(UserReadLater).filter(
        UserReadLater.user_id == user_id,
        UserReadLater.book_id == book_id
    ).first()
    
    if existing_entry:
        db.delete(existing_entry)
        action = "deleted"
        db.commit()
    else:
        new_entry = UserReadLater(user_id=user_id, book_id=book_id)
        db.add(new_entry)
        db.commit()
        action = "created"

    return {"status": "ok", "action": action}

def get_user_readlater_per_book(db: Session, user_id: int, book_id: int) -> bool:
    """Get the is_readlater flag on a user's review record for a given book."""
    existing_entry = db.query(UserReadLater).filter(
        UserReadLater.user_id == user_id,
        UserReadLater.book_id == book_id
    ).first()

    if existing_entry:
        return True
    else:
        return False
    
def get_user_readlater(db: Session, user_id: int):
    """Get the is_readlater flag on a user's review record for a given book."""
    existing_entry = db.query(UserReadLater).options(joinedload(UserReadLater.book).joinedload(Book.author)).filter(
        UserReadLater.user_id == user_id,
    ).all()

    if existing_entry:
        return [entry.book for entry in existing_entry]
    else:
        return []