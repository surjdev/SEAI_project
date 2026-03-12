from sqlalchemy.orm import Session, joinedload
from Database.Model.models import User


def get_all_users(db: Session) -> list[dict]:
    # ใช้ joinedload เพื่อดึง reviews และ readlater มาใน Query เดียว
    users = db.query(User).options(
        joinedload(User.reviews),
        joinedload(User.readlater)
    ).order_by(User.id).limit(100).all() 

    result = []

    for user in users:
        
        readlater_ids = [rl.book_id for rl in user.readlater]
        
        reviews = user.reviews
        book_ratings = [{"book_id": r.book_id, "rating": r.book_rating} for r in reviews if r.book_rating is not None]
        is_favourite = [{"book_id": r.book_id} for r in reviews if r.is_favourite]
        comments = [{"book_id": r.book_id, "comment": r.comment} for r in reviews if r.comment]

        result.append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "birth_year": user.birth_year,
            "location": user.location,
            "user_image": user.user_image,
            "book_rating": book_ratings,
            "is_favourite": is_favourite,
            "user_readlater": readlater_ids,
            "comments": comments,
        })
    return result

