from Database.database import SessionLocal
from Database.Model.User import User, UserBookStatus, Rating
from Database.Model.Comment import Comment
from sqlalchemy.orm import joinedload


def get_all_user():
    db = SessionLocal()
    try:
        users = db.query(User)\
            .options(
                joinedload(User.ratings).joinedload(Rating.book),
                joinedload(User.book_statuses).joinedload(UserBookStatus.book),
                joinedload(User.comments).joinedload(Comment.book)
            )\
            .limit(100)\
            .all()

        user_list = []

        for user in users:

            rated = [
                f"{r.book.title} ({r.book_rating})"
                for r in user.ratings
            ] if user.ratings else []

            favorites = [
                s.book.title
                for s in user.book_statuses if s.is_favorite
            ] if user.book_statuses else []

            wishlists = [
                s.book.title
                for s in user.book_statuses if s.is_wishlist
            ] if user.book_statuses else []

            comment_list = [
                {
                    "book_title": c.book.title,
                    "comment": c.comment
                }
                for c in user.comments
            ] if user.comments else []

            user_list.append({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "birth_date": str(user.birth_date) if user.birth_date else None,
                "location": user.location or "N/A",
                "user_image": user.user_image or "",
                "rated_books": rated,
                "favorite_books": favorites,
                "wishlist_books": wishlists,
                "comments": comment_list,
                "comment_count": len(comment_list)
            })

        return user_list

    finally:
        db.close()
