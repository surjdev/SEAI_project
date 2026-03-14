from sqlalchemy.orm import Session
from sqlalchemy import func, select, or_, case, and_, Float
from Database.database import engine
from Database.Model.models import Book, UserReview, Author, Publisher
from sqlalchemy.orm import joinedload, load_only, contains_eager

def get_book_detail(db: Session, book_id) -> dict:
    book = db.query(Book).options(
        joinedload(Book.reviews).joinedload(UserReview.user),
        joinedload(Book.readlater),
        joinedload(Book.author),
        joinedload(Book.publisher)
    ).filter(Book.id == book_id).first()
    return book

def get_book_details(db: Session, book_reccomend: dict) -> dict:
    result = {}
    for reccomend_type in book_reccomend:
        result[reccomend_type] = []
        for book_id in book_reccomend[reccomend_type]["book_id"]:
            book = get_book_detail(db, book_id)
            result[reccomend_type].append(book)
    return result

_search_index: list[dict] = []

def load_search_index(db: Session):
    """Load all books into memory for fast in-memory search. Call once at startup."""
    global _search_index
    books = (
        db.query(Book)
        .join(Book.author)                          # JOIN แทน subquery
        .join(Book.publisher)
        .options(
            load_only(Book.id, Book.name, Book.image_url),
            contains_eager(Book.author).load_only(Author.name),
            contains_eager(Book.publisher).load_only(Publisher.name),
        )
        .all()
    )
    _search_index = [
        {
            "id":        book.id,
            "name":      book.name or "",
            "image_url": book.image_url or "",
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

    query = query.lower()
    tokens = query.split()
    results = []

    for book in _search_index:
        if all(token in book["_text"] for token in tokens):
            name = book["name"].lower()
            score = 3 if name == query else (2 if name.startswith(query) else 1)
            results.append((book, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [
        {"id": book["id"], 
         "name": book["name"], 
         "image_url": book["image_url"], 
         "author": book["author"], 
         "publisher": book["publisher"], 
         "score": score}
        for book, score in results[:limit]
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