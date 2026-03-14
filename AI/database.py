import os
import asyncio
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def fetch_user_reviews(path: str):
    """
    Download user_reviews from database to csv file asynchronously
    """
    try:
        async with AsyncSessionLocal() as db:
            sql = text("SELECT * FROM user_reviews;")
            result = await db.execute(sql)
            rows = result.mappings().all() 
            df = pd.DataFrame(rows)
            await asyncio.to_thread(df.to_csv, path, index=False)
        return {"download": "success"}
    except Exception as e:
        return {"download": "failed", "error": str(e)}
    
if __name__ == "__main__":
    from model import BUFFER_PATH
    status = asyncio.run(fetch_user_reviews(BUFFER_PATH))
    print(status)