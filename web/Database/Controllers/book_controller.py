from sqlalchemy.orm import Session
from sqlalchemy import func, select, or_, case, and_, Float
from Database.database import engine
from Database.Model.models import Book, UserReview, Author, Publisher
from sqlalchemy.orm import joinedload, load_only, contains_eager

db = Session(engine)

def get_all_books() -> list[dict]:
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

def get_book_detail(book_id,user_id) -> dict:
    # select(Book).where(Book.name == f"&{query}&")
    
    db = Session(engine)
    book = db.query(Book).options(
        joinedload(Book.reviews),
        joinedload(Book.readlater),
        joinedload(Book.author),
        joinedload(Book.publisher)
    )
    
    if not book:
        return {"error": "Book not found"}

    if user_id == None:
        guest_mode = True
        book = book.filter(Book.id == book_id).first()
        user_rate = None
    else:
        guest_mode = False
        book = book.filter(
            Book.id == book_id, 
            UserReview.user_id == user_id).first()
        
        user_review = next((r for r in book.reviews if r.user_id == int(user_id)), None)
        user_rate = user_review.book_rating if user_review else None

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

    return {
        "book_id": book.id,
        "name": book.name,
        "image_url": book.image_url,
        "author_name": book.author.name if book.author else None,
        "publisher_name": book.publisher.name if book.publisher else None,
        "published_year": book.published_year,
        "guest_mode":guest_mode,
        "user_rate" : user_rate,
        "avg_rating": round(float(avg_rating), 2) if avg_rating else None,
        "comments": comments,
    }

_search_index: list[dict] = []

def load_search_index():
    """Load all books into memory for fast in-memory search. Call once at startup."""
    global _search_index
    books = (
        db.query(Book)
        .join(Book.author)
        .join(Book.publisher)
        .options(
            load_only(Book.id, Book.name),
            contains_eager(Book.author).load_only(Author.name),
            contains_eager(Book.publisher).load_only(Publisher.name),
        )
        .all()
    )
    _search_index = [
        {
            "id":        book.id,
            "name":      book.name or "",
            "author":    book.author.name if book.author else "",
            "publisher": book.publisher.name if book.publisher else "",
            "_text":     f"{book.name} {book.author.name if book.author else ''} {book.publisher.name if book.publisher else ''}".lower(),
        }
        for book in books
    ]

def search_book_fast(query: str, limit: int = 10) -> list[dict]:
    """In-memory search using pre-loaded index. Much faster than SQL ILIKE on first hit."""
    if not query or not _search_index:
        return []

    q = query.lower()
    tokens = q.split()
    results = []

    for book in _search_index:
        if all(t in book["_text"] for t in tokens):
            name = book["name"].lower()
            score = 3 if name == q else (2 if name.startswith(q) else 1)
            results.append((book, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [
        {"id": b["id"], "name": b["name"], "author": b["author"], "publisher": b["publisher"], "score": s}
        for b, s in results[:limit]
    ]

def search_book(query: str, limit: int = 10, page: int = 1):
    query = query.strip()
    if not query:
        return []

    # แยก query เป็น tokens สำหรับ multi-word search
    tokens = query.split()
    exact_filter = f"{query}"
    starts_filter = f"{query}%"
    contains_filter = f"%{query}%"

    # Relevance score: exact > starts_with > contains
    relevance = case(
        (Book.name.ilike(exact_filter),    3),
        (Book.name.ilike(starts_filter),   2),
        (Book.name.ilike(contains_filter), 1),
        else_=0
    )

    # Multi-word: ทุก token ต้องตรงกับ name หรือ author หรือ publisher
    token_filters = [
        or_(
            Book.name.ilike(f"%{token}%"),
            Author.name.ilike(f"%{token}%"),        # ← JOIN แล้วใช้ได้เลย
            Publisher.name.ilike(f"%{token}%"),
        )
        for token in tokens
    ]

    offset = (page - 1) * limit

    books = (
        db.query(Book, relevance)
        .join(Book.author)                          # JOIN แทน subquery
        .join(Book.publisher)
        .options(
            load_only(Book.id, Book.name),
            contains_eager(Book.author).load_only(Author.name),
            contains_eager(Book.publisher).load_only(Publisher.name),
        )
        .filter(and_(*token_filters))
        .order_by(relevance.desc())
        .limit(limit)
        .offset((page - 1) * limit)
        .all()
    )

    return [
    {
        "id":        book.id,
        "name":      book.name,
        "author":    book.author.name if book.author else None,
        "publisher": book.publisher.name if book.publisher else None,
        "score":     score,    # optional
    }
    for book, score in books
]