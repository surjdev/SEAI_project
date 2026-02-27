from flask import Flask, request, jsonify, abort
from functools import wraps
# import requests
from model import Recommender, BUFFER_PATH
# import pandas as pd
# from pathlib import Path
# import tqdm

def download_buffer():
    try:
        flag = False
        return {"download": "success"}
    except Exception as e:
        return {"download": "failed", "error": str(e)}

app = Flask(__name__)

INTERNAL_TOKEN = "RECOMMENDER_MODEL_SECRET_KEY"
BACKEND_URL = ""

# initialize data buffer
# in case that the buffer is not exist, download it from the backend
for i in range(10):
    status = download_buffer()
    if status["download"] == "success":
        break
else:
    raise FileNotFoundError("Buffer file not found after 10 attempts")

# initialize recommender
recommender = Recommender()

def require_token(f):
    @wraps(f) # 2. Add this decorator here
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or " " not in auth_header:
            return jsonify({"error": "Missing or malformed token"}), 403
        
        token = auth_header.split(" ")[1]
        if token != INTERNAL_TOKEN:
            return jsonify({"error": "Not allow to call this service"}), 403
        
        return f(*args, **kwargs)
    return wrapper

@app.route("/recommend/api", methods=["POST"])
@require_token
def recommend():
    user_id = request.json.get("user_id")
    limit = request.json.get("limit", 10)
    recommend_book = recommender.recommend(user_id, limit)
    print(recommend_book)
    return jsonify(recommend_book)

@app.route("/recommend/update", methods=["POST"])
@require_token
def update_model():
    status = {}
    status.update(download_buffer())
    status.update(recommender.update())
    return jsonify(status)

@app.route('/upload', methods=['POST'])
def upload_file():
    # 'file' is the key we will use on the sender side
    if 'file' not in request.files:
        return {"error": "No file part in the request"}, 400
    
    file = request.files['file']
    
    if file.filename == '':
        return {"error": "No selected file"}, 400

    file.save(BUFFER_PATH)
    
    return {"message": f"Successfully uploaded {file.filename}"}, 200


########################################################
##                      BACKEND                       ##
########################################################
# SERVER_URL = "http://<COMPUTER_B_IP>:5000/upload"
# filename = "my_data.csv"
# try:
#     with open(filename, "rb") as f:
#         # The key 'file' here must match request.files['file'] in the Flask code
#         files = {'file': f}
#         response = requests.post(SERVER_URL, files=files)
    
#     print(f"Status: {response.status_code}")
#     print(f"Response: {response.json()}")
# except Exception as e:
#     print(f"An error occurred: {e}")


def transform_data(data:dict):
    pass
    return data
    

if __name__ == "__main__":
    app.run(port=5002, debug=True)