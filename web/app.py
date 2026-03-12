
import os
from flask import Flask, render_template, request, jsonify
from flask_caching import Cache

from flask_login import LoginManager, UserMixin, login_required, current_user
from auth import auth_bp, oauth

from Database.database import get_db
from Database.Controllers import get_all_books, get_all_users
from Database.Controllers.book_controller import get_book_detail, load_search_index, search_book_fast
from Database.Controllers.user_readlater_controller import update_user_readlater
from Database.Controllers.user_review_controlloer import update_user_favorite, update_user_review
import re

# config
app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv('FLASK_SECRET_ID')
app.config["CACHE_TYPE"] = "SimpleCache"   # "RedisCache" for Redis
app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # second

# cache
cache = Cache(app)

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

@app.route("/books")
@cache.cached(timeout=300, key_prefix="all_books")
def books_view():
    with get_db() as db:  
        books = get_all_books(db)
        return render_template("books.html", books=books)

@app.route("/users")
@cache.cached(timeout=300, key_prefix="all_users")
def users_view():
    with get_db() as db:
        users = get_all_users(db)
        return render_template("users.html", users=users)

@app.route("/review", methods=["POST"])
def review():
    # Accept both JSON body and form data
    data = request.get_json(silent=True) or request.form

    user_id = data.get("user_id")
    book_id = data.get("book_id")
    rating  = data.get("rating")
    comment = data.get("comment", "").strip()

    # ── Validate required fields ──────────────────────────────────────────────
    if not user_id or not book_id:
        return jsonify({"error": "Missing required fields 'user_id' and 'book_id'"}), 400

    if not rating:
        return jsonify({"error": "Missing required field 'rating'"}), 400

    try:
        user_id = int(user_id)
        book_id = int(book_id)
        rating  = int(rating)
    except (ValueError, TypeError):
        return jsonify({"error": "'user_id', 'book_id', and 'rating' must be integers"}), 400

    if not (1 <= rating <= 10):
        return jsonify({"error": "'rating' must be between 1 and 10"}), 400

    # ── Upsert the review ─────────────────────────────────────────────────────
    with get_db() as db:
        result = update_user_review(db, user_id, book_id, rating, comment)
        return jsonify(result), 200



@app.route('/favorite', methods=['POST'])
def favorite():
    # Accept JSON body or form data
    data = request.form

    # Accept either correct `user_id` or possible typo `usei_id`
    user_id = data.get('user_id')
    book_id = data.get('book_id')

    # Validate required fields
    if not user_id or not book_id:
        return jsonify({"error": "Missing required fields 'user_id' and 'book_id'"}), 400
    with get_db() as db:
        # Here you would typically check if the user and book exist in the database
         status = update_user_favorite(db, user_id, book_id)
         return status

@app.route('/readlater', methods=['POST'])
def readlater():
    # Similar implementation to favorite, but for read later functionality
    data = request.form

    user_id = data.get('user_id')
    book_id = data.get('book_id')

    if not user_id or not book_id:
        return jsonify({"error": "Missing required fields 'user_id' and 'book_id'"}), 400
    with get_db() as db:
        # Implement the logic to add/remove the book from the user's read later list
        # This would involve checking if the entry exists and then adding or removing it accordingly
        status = update_user_readlater(db, user_id, book_id)  # Placeholder response
        return status
@app.route("/search-test")
def search_test():
    return render_template("search_test.html")

################################### Route ##################################

@app.route("/book_detail")
@cache.cached(timeout=300, key_prefix=lambda: f"book_{request.args.get('book_id')}_{user_id}")
def book_detail():
    book_id = request.args.get('book_id')
    return jsonify(get_book_detail(book_id=book_id, user_id=user_id))

# protect injection
def sanitize(query: str) -> str:
    query = re.sub(r'[%_\\]', '', query)  # escape LIKE wildcards
    return query.strip()[:100]

@app.route('/search')
def book_search():
    query = sanitize(request.args.get('query', ''))
    return jsonify(search_book_fast(query))

if __name__ == "__main__":
    load_search_index()  # build in-memory index once at startup
    app.run(debug=True)



