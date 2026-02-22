from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String(255), primary_key=True)
    username = Column(String(50))
    email = Column(String(100))
    birth_date = Column(Date)
    location = Column(String(150))
    user_image = Column(String(2083))
    
    ratings = relationship("Rating", back_populates="user")
    book_statuses = relationship("UserBookStatus", back_populates="user")
    comments = relationship("Comment", back_populates="user")

class UserBookStatus(Base):
    __tablename__ = 'user_book_status'
    user_id = Column(String(255), ForeignKey('users.user_id'), primary_key=True)
    book_id = Column(String(13), ForeignKey('books.book_id'), primary_key=True)
    is_favorite = Column(Boolean, default=False)
    is_wishlist = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="book_statuses")
    book = relationship("Book", back_populates="statuses")

class Rating(Base):
    __tablename__ = 'rating'
    user_id = Column(String(255), ForeignKey('users.user_id'), primary_key=True)
    book_id = Column(String(13), ForeignKey('books.book_id'), primary_key=True)
    book_rating = Column(Integer)
    
    book = relationship("Book", back_populates="ratings")
    user = relationship("User", back_populates="ratings") 

