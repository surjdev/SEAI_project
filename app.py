import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager, UserMixin, login_required, current_user
from auth import auth_bp, oauth

load_dotenv()

app = Flask(__name__, template_folder='test_template') #ถ้าจะใช้ frontend จริงๆ ให้ลบ template_folder='test_template' ออกเด้อ
app.secret_key = os.getenv('FLASK_SECRET_ID')

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# OAuth Setup
oauth.init_app(app)
app.register_blueprint(auth_bp, url_prefix='/auth')

# Simple User class for demonstration
class User(UserMixin):
    def __init__(self, id, name):
        self.id = id
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id, name="User Name")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/protected')
@login_required 
def secret_page():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)