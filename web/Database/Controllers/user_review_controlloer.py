from sqlalchemy.orm import Session, joinedload
from Database.Model.models import UserReview, Book

def update_user_favorite(db: Session, user_id: int, book_id: int) -> dict:
    """Toggle the is_favourite flag on a user's review record for a given book.
    Creates the record if it does not exist yet."""
    existing_review = db.query(UserReview).filter(
        UserReview.user_id == user_id,
        UserReview.book_id == book_id
    ).first()

    if existing_review:
        if existing_review.is_favourite:
            existing_review.is_favourite = False
        else:
            existing_review.is_favourite = True
        db.commit()
        action = "updated"
    else:
        new_review = UserReview(user_id=user_id, book_id=book_id, is_favourite=True)
        db.add(new_review)
        db.commit()
        action = "created"

    return {"status": "ok", "action": action}

def update_user_review(db: Session, user_id: int, book_id: int, rating: int, comment: str) -> dict:
    """Toggle the is_favourite flag on a user's review record for a given book.
    Creates the record if it does not exist yet."""
    existing_review = db.query(UserReview).filter(
        UserReview.user_id == user_id,
        UserReview.book_id == book_id
    ).first()

    if existing_review:
        existing_review.book_rating = rating
        existing_review.comment = comment
        db.commit()
        action = "updated"
    else:
        new_review = UserReview(user_id=user_id, book_id=book_id, book_rating=rating, comment=comment)
        db.add(new_review)
        db.commit()
        action = "created"

    return {"status": "ok", "action": action}

def get_user_favorite_per_book(db: Session, user_id: int, book_id: int) -> bool:
    """Get the is_favourite flag on a user's review record for a given book."""
    existing_review = db.query(UserReview).filter(
        UserReview.user_id == user_id,
        UserReview.book_id == book_id
    ).first()

    if existing_review:
        return existing_review.is_favourite
    else:
        return False
    
def get_user_favorite(db: Session, user_id: int):
    """Get the is_favourite flag on a user's review record for a given book."""
    existing_entry = db.query(UserReview).options(joinedload(UserReview.book).joinedload(Book.author)).filter(
        UserReview.user_id == user_id,
        UserReview.is_favourite == True
    ).all()

    if existing_entry:
        return [entry.book for entry in existing_entry]
    else:
        return []
