from sqlalchemy.orm import Session, joinedload
from Database.Model.models import User

def user_in_database(db: Session, google_user_info: dict):
    user = db.query(User).filter(User.email == google_user_info['email']).first()
    return user

def login_or_register_user(db: Session, google_user_info: dict):
    user = user_in_database(db, google_user_info)
    
    if user:
        return user
    try:
        new_user = User(
            username=google_user_info.get('name'),
            email=google_user_info.get('email'),
            user_image=google_user_info.get('picture')
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise e
