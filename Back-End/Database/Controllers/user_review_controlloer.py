from sqlalchemy.orm import Session
from Database.Model.models import UserReview

def update_user_favorite(db: Session, user_id: int, book_id: int) -> dict:
    # Find existing user review for the given user and book
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
    else:
        # If no review exists, create a new one marked as favorite
        new_review = UserReview(user_id=user_id, book_id=book_id, is_favorite=True)
        db.add(new_review)
        db.commit()
    return status