import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify , request
from flask_login import LoginManager, UserMixin, login_required, current_user
from auth import auth_bp, oauth

#test database and models
from database import SessionLocal
from models.Book import Book

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
def book_index():
    db = SessionLocal()
    try:
        books = db.query(Book).all()
        return render_template('book.html', books=books)
    finally:
        db.close()

#test api
@app.route('/api/books', methods=['GET'])
def get_books():
    db = SessionLocal()
    books = db.query(Book).all()
    db.close()
    return jsonify([{"id": b.book_id, "title": b.title} for b in books])

if __name__ == '__main__':
    app.run(debug=True)