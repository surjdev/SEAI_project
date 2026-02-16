import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify , request
from flask_login import LoginManager, UserMixin, login_required, current_user
from auth import auth_bp, oauth

# database and models
from database import SessionLocal
from models.Book import Book
from Controllers.book_controller import get_books_formatted

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_ID') # Keep this safe!

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# OAuth Setup
oauth.init_app(app)
app.register_blueprint(auth_bp, url_prefix='/auth')

# Simple User class for demonstration
class User(UserMixin):
    def __init__(self, id, name):
        self.id = id
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    # In a real app, query your Database: return User.query.get(user_id)
    return User(id=user_id, name="User Name")

@app.route('/')
def index():
    return f"Hello {current_user.name if current_user.is_authenticated else 'Guest'}!"

@app.route('/protected')
@login_required  # This protects the page!
def secret_page():
    return "This is a hidden family page only for logged-in users."

#test database and models
@app.route('/books')
def books_page():
    # หน้าที่ของมันมีแค่ "ส่งหน้ากาก HTML" ไปให้ Browser
    # แล้วเดี๋ยว JavaScript ใน HTML จะทำหน้าที่ไปคุยกับ API เอง
    return render_template('book.html') 


@app.route('/api/books')
def get_books_api():
    data = get_books_formatted() 
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(debug=True,host="10.48.108.14" ,port=5000)