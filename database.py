import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

load_dotenv()

DB_USER = os.getenv('USER')
DB_PASS = os.getenv('PASSWORD')
DB_HOST = os.getenv('HOST')
DB_PORT = os.getenv('PORT')
DB_NAME = os.getenv('DATABASE')


# app = Flask(__name__)
# conn = psycopg2.connect(
#           host = DB_HOST,
#           port = DB_PORT,
#           database = DB_NAME,
#           user = DB_USER,
#           password = DB_PASS
# )

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ฟังก์ชันสำหรับดึง Database Session
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# cur = conn.cursor()
# @app.route('/')
# def index():
#           cur.execute("SELECT * FROM books")
#           records = cur.fetchall()
#           return get_db()
# app.run(debug=True, port=5000)
# cur.close()
# conn.close()