from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# # แบบที่ 1 query ปกติ
# @app.route('/search1')
# def search_book1():
#     return render_template('search_book1.html')

# # แบบที่ 2 query ทุกครั้งที่พิมพ์
# @app.route('/search2')
# def search_book2():
#     return render_template('search_book2.html')

# !!!!!!!!! ส่วนนี้คือการจำลองจาก backend !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# สมมติฐานข้อมูลจำลอง Let's say ว่ามาจาก Database
books = [
    {"id": 1, "title": "Python 101", "author": "John Doe", "avg_rating": 4.5, "num_ratings": 1004},
    {"id": 2, "title": "Flask Web Development", "author": "Jane Smith", "avg_rating": 4.2, "num_ratings": 80},
    {"id": 3, "title": "Data Science Basics", "author": "Alex Lee", "avg_rating": 4.8, "num_ratings": 120},
    {"id": 4, "title": "หนังสือสอนคนดําว่ายนํ้า", "author": "Kasidit Boonsaner", "avg_rating": 4.8, "num_ratings": 65825},
    {"id": 5, "title": "Gris", "author": "Mabel", "avg_rating": 4.2, "num_ratings": 25},
    {"id": 6, "title": "VALORANT", "author": "Pimma", "avg_rating": 4.15, "num_ratings": 150000},
    {"id": 7, "title": "แม่คุณตัวใหญ่", "author": "Sunny", "avg_rating": 4.15, "num_ratings": 150000},
    
]
# avg_rating = SUM(all ratings for that book) / COUNT(ratings)

# Mock comments, keyed by book_id
comments = {
    1: [
        {"username": "Nob",        "rating": 4, "text": "ตรงนี้ผมว่าช้างทําดีนะ!", "profileImage": None},
        {"username": "GOD OF MEME", "rating": 5, "text": "ปืนใหญ่ของเธอน่ะ ใส่เข้ามาในตัวชั้นได้เลย!", "profileImage": None},
    ],
    2: [],
    3: [],
    4: [
        {"username": "Nob",        "rating": 5, "text": "ยังไม่ได้อ่านครับ ให้ 5 ไปก่อนเห็นว่าช้างเป็นคนแต่ง", "profileImage": None},
    ],
}



@app.route('/')
def landing_page():
    user_data = {
        "firstName": "Guest", 
        "profileImage": None       
    }
    return render_template('landing_page.html', user=user_data)

@app.route('/home')
def homepage():
    user_data = {
        "Name": "Guest",
        "profileImage": None
    }
    return render_template('homepage.html', books=books, user=user_data)

@app.route('/search')
def search_book2():
    user_data = {
        "firstName": "Guest", 
        "profileImage": None       
    }
    return render_template('search_book.html', user=user_data)

@app.route('/api/search')
def book_query():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
 
    results = [
        book for book in books 
        if query in book['title'].lower() or query in book['author'].lower()
    ]
    return jsonify(results)

@app.route('/api/rate', methods=['POST'])
def rate_book():
    data = request.get_json()
    book_id = data.get('book_id')
    new_rating = data.get('rating')

    # Validate input
    if not book_id or not new_rating or not (1 <= int(new_rating) <= 5):
        return jsonify({"error": "Invalid input"}), 400

    # Find the book in mock data
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Incremental average formula:
    # new_avg = (old_avg * old_count + new_rating) / (old_count + 1)
    old_avg   = book['avg_rating']
    old_count = book['num_ratings']
    new_count = old_count + 1
    new_avg   = round((old_avg * old_count + int(new_rating)) / new_count, 2)

    # Update mock data in-memory
    book['avg_rating']  = new_avg
    book['num_ratings'] = new_count

    return jsonify({
        "avg_rating": new_avg,
        "num_rating": new_count   # frontend formats with toLocaleString()
    })

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    # Find book by id
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return "Book not found", 404
    

     # Enrich with extra detail fields
    book.update({
        "avg_rating": book.get("avg_rating", 0),
        "num_rating": book.get("num_ratings", 0),
        "description": "คําอธิบายหนังสือเล่มนี้ ..."
    })
    
    user_data = {"firstName": "Guest", "profileImage": None}
    book_comments = comments.get(book_id, [])
    return render_template('book_detail.html', book=book, user=user_data, comments=book_comments)

@app.route('/api/comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    book_id  = data.get('book_id')
    username = data.get('username', 'Anonymous')
    rating   = int(data.get('rating', 0))
    text     = data.get('text', '').strip()

    if not book_id or not text:
        return jsonify({"error": "book_id and text are required"}), 400
    if not any(b['id'] == book_id for b in books):
        return jsonify({"error": "Book not found"}), 404

    new_comment = {"username": username, "rating": rating, "text": text, "profileImage": None}
    comments.setdefault(book_id, []).insert(0, new_comment)  # newest first
    return jsonify(new_comment), 201

if __name__ == '__main__':
    app.run(debug=True)