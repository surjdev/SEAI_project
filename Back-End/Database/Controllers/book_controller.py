from sqlalchemy.orm import Session
from sqlalchemy import func
from Database.Model.models import Book, UserReview
from sqlalchemy.orm import joinedload

def get_all_books(db: Session) -> list[dict]:
    # 1. ใช้ joinedload ดึงความสัมพันธ์ทั้งหมดมาใน Query เดียว
    books = db.query(Book).options(
        joinedload(Book.reviews),
        joinedload(Book.readlater),
        joinedload(Book.author),
        joinedload(Book.publisher)
    ).limit(100).all()

    result = []

    for book in books:
        # รายชื่อ User ID ที่กด Favourite
        fav_users = [
            r.user_id for r in book.reviews if r.is_favourite
        ]

        # รายชื่อ User ID ที่กด Read Later
        readlater_users = [
            rl.user_id for rl in book.readlater
        ]

        # Average Rating
        avg_rating = (
            db.query(func.avg(UserReview.book_rating))
            .filter(UserReview.book_id == book.id)
            .scalar()
        )

        # รายการความคิดเห็น (User ID + ข้อความ)
        comments = [
            {"user_id": r.user_id, "text": r.comment}
            for r in book.reviews if r.comment
        ]

        result.append({
            "book_id": book.id,
            "name": book.name,
            "image_url": book.image_url,
            "author_name": book.author.name if book.author else None,
            "publisher_name": book.publisher.name if book.publisher else None,
            "published_year": book.published_year,
            "favourite_users": fav_users,       
            "readlater_users": readlater_users, 
            "avg_rating": round(float(avg_rating), 2) if avg_rating else None,
            "comments": comments,
        })

    return result


