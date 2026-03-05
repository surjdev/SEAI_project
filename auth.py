import os
from flask import Blueprint, url_for, redirect, session
from authlib.integrations.flask_client import OAuth
from flask_login import login_user, logout_user

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()

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
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info:
        session['user_id'] = user_info['sub']
        session['user_name'] = user_info['name']  
        session['user_email'] = user_info['email']
        
        from app import User
        user = User(id=user_info['sub'], name=user_info['name'])
        login_user(user)
    
    return redirect('/')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')