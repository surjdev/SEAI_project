from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# 1. ตารางกลาง (Mapping Table)
class BookAuthor(Base):
    __tablename__ = 'book_authors'
    book_id = Column(String, ForeignKey('books.book_id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.author_id'), primary_key=True)

# 2. คลาส Book
class Book(Base):
    __tablename__ = 'books'
    book_id = Column(String, primary_key=True)
    title = Column(String)
    
    # แก้ไขตรงนี้: ใช้ secondary='book_authors' (ต้องมี ' ' ครอบชื่อตาราง)
    authors = relationship("Author", secondary='book_authors', back_populates="books")

# 3. คลาส Author
class Author(Base):
    __tablename__ = 'authors'
    author_id = Column(Integer, primary_key=True)
    author_name = Column(String)
    
    # แก้ไขตรงนี้เหมือนกันครับ
    books = relationship("Book", secondary='book_authors', back_populates="authors")
    