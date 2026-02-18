from flask import Flask, render_template, request, jsonify

app = Flask(__name__)



# แบบที่ 1 query ปกติ
@app.route('/search1')
def search_book1():
    return render_template('search_book1.html')

# แบบที่ 2 query ทุกครั้งที่พิมพ์
@app.route('/search2')
def search_book2():
    return render_template('search_book2.html')

# !!!!!!!!! ส่วนนี้คือการจำลองจาก backend โปรดสื่อสารกัน !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# สมมติฐานข้อมูลจำลอง
books = [
    {"id": 1, "title": "Python 101", "author": "John Doe"},
    {"id": 2, "title": "Flask Web Development", "author": "Jane Smith"},
    {"id": 3, "title": "Data Science Basics", "author": "Alex Lee"},
]

@app.route('/api/search')
def book_query2():
    query = request.args.get('q', '').lower()
    
    # Filter logic
    results = [
        book for book in books 
        if query in book['title'].lower() or query in book['author'].lower()
    ]
    
    # Return data as JSON
    return jsonify(results)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

if __name__ == '__main__':
    app.run(debug=True)