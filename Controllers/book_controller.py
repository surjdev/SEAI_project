from models.Book import Book
from database import SessionLocal


from sqlalchemy.orm import joinedload

def get_books_formatted():
    db = SessionLocal()
    try:
        books = db.query(Book).options(joinedload(Book.authors)).limit(100).all()
        
        return [{
            "book_id": b.book_id,
            "title": b.title,
            # แสดงรายชื่อผู้เขียน (ถ้ามี)
            "authors": [a.author_name for a in b.authors] if b.authors else ["Unknown"]
        } for b in books]
    finally:
        db.close()