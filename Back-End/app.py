import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify , request
from flask_login import LoginManager, UserMixin, login_required, current_user

from flask_cors import CORS

# Controllers
from Database.Controller.user_controller import get_all_user
from Database.Controller.book_controller import get_books_formatted


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_ID') # Keep this safe!
CORS(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# OAuth Setup
oauth.init_app(app)
app.register_blueprint(auth_bp, url_prefix='/auth')

# Simple User class for demonstration
class LoginUser(UserMixin):
    def __init__(self, id, name):
        self.id = id
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    # In a real app, query your Database: return User.query.get(user_id)
    return LoginUser(id=user_id, name="User Name")

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
    return render_template('book.html') 

@app.route('/api/books')
def get_books_api():
    data = get_books_formatted() 
    return jsonify(data)

@app.route('/api/users') 
def get_all_users_api():
    data = get_all_user() 
    return jsonify(data)

@app.route('/all-users')
def all_users_page():
    return render_template('all_users.html')

if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(debug=True,host="10.48.108.14" ,port=5000)