from Database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Book(Base):
    __tablename__ = 'books'
    book_id = Column(String(13), primary_key=True)
    title = Column(String(500))
    publisher_id = Column(Integer, ForeignKey('publishers.publisher_id'))
    published_year = Column(Integer)
    image_url = Column(String(2083))
    
    # Relationships
    authors = relationship("Author", secondary='book_authors', back_populates="books")
    publisher = relationship("Publisher")
    # เชื่อมไปหา Rating และ Status เพื่อใช้คำนวณ count/avg
    ratings = relationship("Rating", back_populates="book")
    statuses = relationship("UserBookStatus", back_populates="book")
    comments = relationship("Comment", back_populates="book")

class Author(Base):
    __tablename__ = 'authors'
    author_id = Column(Integer, primary_key=True)
    author_name = Column(String(255))

    books = relationship("Book", secondary='book_authors', back_populates="authors")

class BookAuthor(Base):
    __tablename__ = 'book_authors'
    book_id = Column(String(13), ForeignKey('books.book_id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.author_id'), primary_key=True)

class Publisher(Base):
    __tablename__ = 'publishers'
    publisher_id = Column(Integer, primary_key=True)
    publisher_name = Column(String(255))



