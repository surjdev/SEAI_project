from sqlalchemy import func
from database import SessionLocal
from models.Book import Book
from models.User import UserBookStatus, Rating
from models.Comment import Comment 
from sqlalchemy.orm import selectinload




def get_books_formatted():
    db = SessionLocal()
    try:
        # โหลด relation ทีเดียว
        books = db.query(Book)\
            .options(
                selectinload(Book.authors),
                selectinload(Book.publisher),
                selectinload(Book.comments)
            )\
            .limit(100)\
            .all()

        # --- aggregate ล่วงหน้าแบบ group by ---
        rating_map = dict(
            db.query(
                Rating.book_id,
                func.avg(Rating.book_rating)
            ).group_by(Rating.book_id).all()
        )

        favorite_map = dict(
            db.query(
                UserBookStatus.book_id,
                func.count(UserBookStatus.user_id)
            )
            .filter(UserBookStatus.is_favorite == True)
            .group_by(UserBookStatus.book_id)
            .all()
        )

        wishlist_map = dict(
            db.query(
                UserBookStatus.book_id,
                func.count(UserBookStatus.user_id)
            )
            .filter(UserBookStatus.is_wishlist == True)
            .group_by(UserBookStatus.book_id)
            .all()
        )

        books_list = []

        for b in books:

            comment_list = [
                {
                    "user_id": c.user_id,
                    "comment": c.comment,
                    "created_at": str(c.created_at)
                }
                for c in b.comments
            ] if b.comments else []

            books_list.append({
                "book_id": b.book_id,
                "title": b.title,
                "image_url": b.image_url,
                "author_name": ", ".join([a.author_name for a in b.authors]) if b.authors else "Unknown",
                "publisher_name": b.publisher.publisher_name if b.publisher else "N/A",
                "published_year": b.published_year,
                "favorite_count": favorite_map.get(b.book_id, 0),
                "wishlist_count": wishlist_map.get(b.book_id, 0),
                "avg_rating": round(float(rating_map.get(b.book_id, 0) or 0), 2),
                "comments": comment_list,
                "comment_count": len(comment_list)
            })

        return books_list

    finally:
        db.close()


