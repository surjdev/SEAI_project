from flask import Flask, render_template
from Database.database import get_db
from Database.Controllers import get_all_books, get_all_users

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


if __name__ == "__main__":
    app.run(debug=True)
    