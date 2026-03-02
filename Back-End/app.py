from flask import Flask, render_template, request, jsonify
from flask_caching import Cache

from Database.database import get_db
from Database.Controllers import get_all_books, get_all_users
from Database.Controllers.book_controller import get_book_detail, load_search_index, search_book_fast

import re

# config
app = Flask(__name__, template_folder="templates")
app.config["CACHE_TYPE"] = "SimpleCache"   # "RedisCache" for Redis
app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # second

# cache
cache = Cache(app)

# login
login_required = False
if login_required:
    user_id = 12
user_id = None

################################### DEBUG ###################################

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
    