from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.schemas import UserCreate, UserOut, UserUpdate
from app.services.deps import get_db, get_user_repo, get_current_user, require_admin
from app.models.models import User
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    repo = get_user_repo(db)
    hashed = hash_password(payload.password)
    user = repo.create(
        name=payload.name,
        email=payload.email,
        verified_author=payload.verified_author,
        avatar_url=payload.avatar_url,
        hashed_password=hashed,
        is_admin=False,
    )
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        verified_author=user.verified_author,
        avatar_url=user.avatar_url,
        registered_at=user.registered_at,
        is_admin=user.is_admin,
    )

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = get_user_repo(db)
    user = repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_admin and current_user.id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        verified_author=user.verified_author,
        avatar_url=user.avatar_url,
        registered_at=user.registered_at,
        is_admin=user.is_admin,
    )

@router.get("/", response_model=list[UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    repo = get_user_repo(db)
    users = repo.list(skip=skip, limit=limit)
    return [
        UserOut(
            id=u.id,
            name=u.name,
            email=u.email,
            verified_author=u.verified_author,
            avatar_url=u.avatar_url,
            registered_at=u.registered_at,
            is_admin=u.is_admin,
        )
        for u in users
    ]

@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = get_user_repo(db)
    target = repo.get(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_admin and current_user.id != target.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    fields = payload.dict(exclude_unset=True)
    if not current_user.is_admin:
        fields.pop("verified_author", None)
    updated = repo.update(user_id, **fields)
    return UserOut(
        id=updated.id,
        name=updated.name,
        email=updated.email,
        verified_author=updated.verified_author,
        avatar_url=updated.avatar_url,
        registered_at=updated.registered_at,
        is_admin=updated.is_admin,
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    repo = get_user_repo(db)
    ok = repo.delete(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return None