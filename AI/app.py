from flask import Flask, request, jsonify
from functools import wraps
from model import Recommender, BUFFER_PATH
from download_buffer import fetch_user_reviews
import asyncio

print("Initializing AI API server...")

INTERNAL_TOKEN = "RECOMMENDER_MODEL_SECRET_KEY"

async def download_buffer(buffer_path, max_attempts=5, timeout=10):
    attempt_count = 0
    status = {}
    while not buffer_path.exists():
        if attempt_count >= max_attempts:
            status = {"download": "failed"}
        
        try:
            print(f"Attempt {attempt_count + 1}: Querying database...")
            status = await asyncio.wait_for(fetch_user_reviews(buffer_path), timeout=timeout)
            
            if status.get("download") == "success":
                print("Download successful.")
                return status
        except asyncio.TimeoutError:
            print(f"Request timed out after {timeout} seconds. Retrying...")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
        attempt_count += 1

if not BUFFER_PATH.exists():
    status = asyncio.run(download_buffer(BUFFER_PATH))
    if status.get("download") == "failed":
        FileNotFoundError(f"Buffer file '{BUFFER_PATH}' not found")

print("Buffer file is ready. Starting server...")

app = Flask(__name__)

# initialize recommender
recommender = Recommender()

def require_token(f):
    @wraps(f)
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
    user_id = request.form.get("user_id")
    limit = request.form.get("limit", 10, type=int)
    recommendations = recommender.recommend(user_id, limit)
    return jsonify(recommendations)

@app.route("/recommend/update", methods=["POST"])
@require_token
def update_model():
    status = asyncio.run(download_buffer(BUFFER_PATH))
    if status.get("download") == "success":
        BUFFER_PATH.unlink(missing_ok=True)
        status.update(recommender.update())
    return jsonify(status)

def transform_data(data:dict):
    pass
    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)