
import os
import re
import requests

from flask import Flask, render_template, request, jsonify
# from flask_caching import Cache
from flask_login import LoginManager, current_user, login_required
from auth import auth_bp, oauth

from Database.database import get_db

from Database.Controllers.book_controller import get_book_detail, load_search_index, search_book_fast, get_book_details
from Database.Controllers.user_readlater_controller import update_user_readlater, get_user_readlater, get_user_readlater_per_book
from Database.Controllers.user_review_controlloer import update_user_favorite, update_user_review, get_user_favorite, get_user_favorite_per_book
from Database.Model.models import User
from Database.database import sync_sequences

# AI Service
AI_SERVICE_URL = os.getenv('AI_API_URL')
INTERNAL_TOKEN = os.getenv('INTERNAL_TOKEN')

# config
app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv('FLASK_SECRET_ID')
app.config["CACHE_TYPE"] = "SimpleCache"   # "RedisCache" for Redis
app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # second

# sync sequences
with get_db() as db:
    sync_sequences(db)

# cache
# cache = Cache(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = "auth.login"

# OAuth Setup
oauth.init_app(app)
app.register_blueprint(auth_bp, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return db.query(User).get(int(user_id))

########################### Page routes ###########################

def check_user_auth():
    is_auth = current_user.is_authenticated
    user_data = {
        "mode":"logged_in" if is_auth else "Guest", 
        "user":current_user if is_auth else None
    }  
    return user_data

@app.route('/')
def landing_page():
    user_data = check_user_auth()
    return render_template('landing_page.html', user=user_data)

recommend_name_mapper = {
    "model_plus": "SVD Plus",
    "model": "SVD+Favorite",
    "most_controversial": "Most Controversial",
    "most_popular": "Most Popular",
    "most_rated": "Most Rated"
}
@app.route('/home')
def home_page():
    user_data = check_user_auth()
    user_id = user_data["user"].id if user_data["mode"] == "login" else None
    reccomend_book = requests.post(f"{AI_SERVICE_URL}/recommend/api", data={"user_id": user_id}, headers={"Authorization": f"Bearer {INTERNAL_TOKEN}"})
    reccomend_book = reccomend_book.json()
    with get_db() as db:
        reccomend_book = get_book_details(db, reccomend_book)
        for recommend_type in reccomend_book:
            reccomend_book[recommend_name_mapper[recommend_type]] = reccomend_book.pop(recommend_type)
    return render_template('homepage.html', user=user_data, recommend_book=reccomend_book)

@app.route('/search')
def search_page():
    user_data = check_user_auth()
    return render_template('search_book.html', user=user_data)

@app.route('/profile')
@login_required
def profile_page():
    user_data = check_user_auth()
    return render_template('profile_page.html', user=user_data)

@app.route('/book/<int:book_id>')
def book_detail_page(book_id):
    user_data = check_user_auth()
    with get_db() as db:
        book = get_book_detail(db, book_id)
    book_rating = [review.book_rating for review in book.reviews if review.book_rating is not None]
    book_review_count = len(book.reviews)
    book_stat = {
        "avg_rating": sum(book_rating) / len(book_rating) if book_rating else 0,
        "review_count": book_review_count
    }
    is_favorite = False
    is_readlater = False
    if user_data["mode"] == "logged_in":
        with get_db() as db:
            is_favorite = get_user_favorite_per_book(db, user_data["user"].id, book_id)
            is_readlater = get_user_readlater_per_book(db, user_data["user"].id, book_id)
    return render_template('book_detail.html', book=book, user=user_data, book_stat=book_stat, is_favorite=is_favorite, is_readlater=is_readlater)

@app.route('/favorite')
@login_required
def favorite_page():
    user_data = check_user_auth()
    with get_db() as db:
        favorite_books = get_user_favorite(db, user_data["user"].id)
    return render_template('favorite_page.html', user=user_data, favorite_books=favorite_books)

@app.route('/readlater')
@login_required
def readlater_page():
    user_data = check_user_auth()
    with get_db() as db:
        readlater_books = get_user_readlater(db, user_data["user"].id)
    return render_template('readlater_page.html', user=user_data, readlater_books=readlater_books)
########################### Service routes ###########################

@app.route('/favorite', methods=['POST'])
@login_required
def favorite():
    # Accept JSON body or form data
    data = request.form
    book_id = data.get('book_id')

    # Validate required fields
    if not book_id:
        return jsonify({"error": "Missing required fields 'book_id'"}), 400
    with get_db() as db:
         status = update_user_favorite(db, current_user.id, book_id)
         return status

@app.route('/readlater', methods=['POST'])
@login_required
def readlater():
    # Similar implementation to favorite, but for read later functionality
    data = request.form
    book_id = data.get('book_id')

    if not book_id:
        return jsonify({"error": "Missing required fields 'book_id'"}), 400
    with get_db() as db:
        status = update_user_readlater(db, current_user.id, book_id)
        return status

@app.route('/review', methods=['POST'])
@login_required
def review():
    data = request.form
    print(data)
    book_id = data.get("book_id")
    rating  = data.get("rating")
    comment = data.get("comment", "").strip()

    # ── Validate required fields ──────────────────────────────────────────────
    if not comment or not rating:
        return jsonify({"error": "Missing required fields 'comment' and 'rating'"}), 400
    rating = int(rating)
    rating = rating if rating != 0 else None
    comment = comment if comment else None
    # ── Upsert the review ─────────────────────────────────────────────────────
    with get_db() as db:
        result = update_user_review(db, current_user.id, book_id, rating, comment)
        return jsonify(result), 200

########################### API routes ###########################
# protect injection
def sanitize(query: str) -> str:
    query = re.sub(r'[%_\\]', '', query)  # escape LIKE wildcards
    return query.strip()[:100]

@app.route('/search/engine')
def book_search():
    query = sanitize(request.args.get('query', ''))
    result = search_book_fast(query)
    return jsonify(result)

if __name__ == "__main__":
    with get_db() as db:
        load_search_index(db)  # build in-memory index once at startup
    app.run(host="0.0.0.0", port=5000, debug=False)



