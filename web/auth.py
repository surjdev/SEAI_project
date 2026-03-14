import os
from flask import Blueprint, url_for, redirect, session
from authlib.integrations.flask_client import OAuth
from flask_login import login_user, logout_user
from Database.Controllers.user_controller import login_or_register_user
from Database.database import get_db

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
        with get_db() as db:
            user = login_or_register_user(db, user_info)
        
        # Login user
        login_user(user)

        # session['user_email'] = user.email
        # session['user_id'] = user.id
        # session['user_name'] = user.username  
    return redirect('/home')

@auth_bp.route('/logout')
def logout():
    logout_user()
    # session.pop('user_email', None)
    # session.pop('user_id', None)
    # session.pop('user_name', None)
    return redirect('/home')