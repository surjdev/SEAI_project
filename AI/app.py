import os
import shutil
from flask import Flask, request, jsonify
from functools import wraps
from model import Recommender, BUFFER_PATH
from database import fetch_user_reviews
import asyncio

print("Initializing AI API server...")

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN")

async def download_buffer(file_to_save_path, max_attempts=5, timeout=10):
    attempt_count = 0
    # Initialize a default failure status
    status = {"download": "failed", "reason": "unknown"} 
    
    while attempt_count < max_attempts:
        if file_to_save_path.exists():
            return {"download": "success", "message": "File already exists"}

        try:
            print(f"Attempt {attempt_count + 1}: Querying database...")
            # Capture the actual result from fetch_user_reviews
            result = await asyncio.wait_for(fetch_user_reviews(file_to_save_path), timeout=timeout)
            
            if result and result.get("download") == "success":
                print("Download successful.")
                return result
            
            status = result # Update status with the latest failure info from the DB call
            
        except asyncio.TimeoutError:
            print(f"Request timed out. Retrying...")
            status = {"download": "failed", "reason": "timeout"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            status = {"download": "failed", "reason": str(e)}
            
        attempt_count += 1
    
    return status # Always return a dict after the loop finishes

if not BUFFER_PATH.exists():
    status = asyncio.run(download_buffer(BUFFER_PATH))
    if status.get("download") == "failed":
        raise FileNotFoundError(f"Buffer file '{BUFFER_PATH}' not found")

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
    if not user_id:
        user_id = None
    recommendations = recommender.recommend(user_id, limit)
    return jsonify(recommendations)

@app.route("/recommend/update", methods=["POST"])
@require_token
def update_model():
    temp_name = "temp.csv"
    temp_path = BUFFER_PATH.with_name(temp_name)

    status = asyncio.run(download_buffer(temp_path))

    if status.get("download") == "success":
        BUFFER_PATH.unlink()
        temp_path.rename(BUFFER_PATH)
        status.update(recommender.update())
    else:
        temp_path.unlink(missing_ok=True)

    return jsonify(status)

def transform_data(data:dict):
    pass
    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)