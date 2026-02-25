from Database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Comment(Base):
    __tablename__ = 'comment'

    comment_id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id'))
    book_id = Column(String(13), ForeignKey('books.book_id'))
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="comments")
    book = relationship("Book", back_populates="comments")


