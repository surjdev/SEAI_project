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
# สมมติฐานข้อมูลจำลอง
books = [
    {"id": 1, "title": "Python 101", "author": "John Doe"},
    {"id": 2, "title": "Flask Web Development", "author": "Jane Smith"},
    {"id": 3, "title": "Data Science Basics", "author": "Alex Lee"},
]

@app.route('/search')
def search_book2():
    user_data = {
        "firstName": "First Name", 
        "profileImage": None       
    }
    return render_template('search_book.html', user=user_data)

@app.route('/api/search')
def book_query():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
 
    results = [
        book for book in books_db 
        if query in book['title'].lower() or query in book['author'].lower()
    ]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)