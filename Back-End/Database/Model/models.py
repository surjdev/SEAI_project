from sqlalchemy import (
    Column, Integer, String, Boolean, Text, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from Database.database import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    books = relationship("Book", back_populates="author")


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    books = relationship("Book", back_populates="publisher")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    birth_year = Column(Integer)
    email = Column(String(255), unique=True)
    location = Column(String(255))
    user_image = Column(String(2083))

    reviews = relationship("UserReview", back_populates="user")
    readlater = relationship("UserReadLater", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    name = Column(String(1000), nullable=False)
    published_year = Column(Integer)
    image_url = Column(String(2083))
    author_id = Column(Integer, ForeignKey("authors.id"))
    publisher_id = Column(Integer, ForeignKey("publishers.id"))

    author = relationship("Author", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
    reviews = relationship("UserReview", back_populates="book")
    readlater = relationship("UserReadLater", back_populates="book")


class UserReview(Base):
    __tablename__ = "user_reviews"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    book_rating = Column(
        Integer,
        CheckConstraint("book_rating BETWEEN 1 AND 10")
    )
    comment = Column(Text)
    is_favourite = Column(Boolean, default=False)

    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")


class UserReadLater(Base):
    __tablename__ = "user_readlater"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)

    user = relationship("User", back_populates="readlater")
    book = relationship("Book", back_populates="readlater")