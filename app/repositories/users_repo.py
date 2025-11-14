from sqlalchemy.orm import Session
from app.models.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str, verified_author: bool, avatar_url: str | None, hashed_password: str | None = None, is_admin: bool = False) -> User:
        user = User(
            name=name,
            email=email,
            verified_author=verified_author,
            avatar_url=avatar_url,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def list(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()

    def update(self, user_id: int, **kwargs):
        user = self.get(user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int):
        user = self.get(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True