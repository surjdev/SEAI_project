from flask import Flask, render_template, request, jsonify, abort
from Database.database import get_db
from Database.Controllers import get_all_books, get_all_users, update_user_favorite, update_user_readlater


app = Flask(__name__, template_folder="templates")


@app.route("/books")
def books_view():
    with get_db() as db:  
        books = get_all_books(db)
        return render_template("books.html", books=books)

@app.route("/users")
def users_view():
    with get_db() as db:
        users = get_all_users(db)
        return render_template("users.html", users=users)

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

if __name__ == "__main__":
    app.run(debug=True)



