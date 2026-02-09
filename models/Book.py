from database import Base
from sqlalchemy import Column, Integer, String

class Book(Base):
    __tablename__ = 'books'
    book_id = Column(String, primary_key=True)
    title = Column(String)
