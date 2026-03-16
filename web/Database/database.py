import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from sqlalchemy import text

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def sync_sequences(db_session):
    tables = ['users']
    try:
        for table in tables:
            # SQL to sync sequence based on max ID
            query = text(f"""
                SELECT setval(pg_get_serial_sequence('{table}', 'id'), 
                coalesce((SELECT MAX(id) FROM {table}), 0) + 1, false);
            """)
            db_session.execute(query)
        db_session.commit()
        print("Sequences synced successfully!")
    except Exception as e:
        db_session.rollback()
        print(f"Sequence sync failed: {e}")