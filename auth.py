import os
from dotenv import load_dotenv
from flask import Blueprint, url_for, redirect, session
from authlib.integrations.flask_client import OAuth
from flask_login import login_user, logout_user

load_dotenv()

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()

# Initialize Google OAuth
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@auth_bp.route('/login')
def login():
    redirect_uri = url_for('auth.callback', _external=True)
    print(f"DEBUG: Redirect URI being sent to Google is: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    # In a real app, you'd save this user to your Database here
    # For now, we'll create a simple User object for Flask-Login
    from app import User
    user = User(id=user_info['sub'], name=user_info['name'])
    login_user(user)
    
    return redirect('/')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')