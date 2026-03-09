from sqlalchemy.orm import Session
from Database.Model.models import UserReview

def update_user_favorite(db: Session, user_id: int, book_id: int) -> dict:
    """Toggle the is_favourite flag on a user's review record for a given book.
    Creates the record if it does not exist yet."""
    existing_review = db.query(UserReview).filter(
        UserReview.user_id == user_id,
        UserReview.book_id == book_id
    ).first()
    status = {"god": "ok"}

    if existing_review:
        if existing_review.is_favorite:
            existing_review.is_favorite = False
        else:
            existing_review.is_favorite = True
        db.commit()
        action = "updated"
    else:
        new_review = UserReview(user_id=user_id, book_id=book_id, is_favourite=True)
        db.add(new_review)
        db.commit()
        action = "created"

    return {"status": "ok", "action": action}


def update_user_review(db: Session, user_id: int, book_id: int, rating: int, comment: str) -> dict:
    """Create or update a user's rating and comment for a given book.
    - If the user already has a review for the book, it will be updated.
    - If no review exists yet, a new one will be created.

    Args:
        db:      SQLAlchemy database session.
        user_id: ID of the user submitting the review.
        book_id: ID of the book being reviewed.
        rating:  Integer rating between 1 and 10.
        comment: Text comment for the review.

    Returns:
        A dict with 'status' and 'action' ('created' or 'updated').
    """
    existing_review = db.query(UserReview).filter(
        UserReview.user_id == user_id,
        UserReview.book_id == book_id
    ).first()

    if existing_review:
        # User already reviewed this book — update existing record
        existing_review.book_rating = rating
        existing_review.comment = comment
        db.commit()
        action = "updated"
    else:
        # No review yet — create a new one
        new_review = UserReview(
            user_id=user_id,
            book_id=book_id,
            book_rating=rating,
            comment=comment
        )
        db.add(new_review)
        db.commit()
        action = "created"

    return {"status": "ok", "action": action}
