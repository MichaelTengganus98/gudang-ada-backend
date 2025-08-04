from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserOut, UserLogin
from models.user import User, UserRole
from database import SessionLocal
from auth import hash_password, verify_password, create_access_token, get_current_user, require_role

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.user_id == user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User ID already exists")

    db_user = User(
        user_id=user.user_id,
        name=user.name,
        address=user.address,
        phone_number=user.phone_number,
        password=hash_password(user.password),
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == login_data.user_id).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID or password",
        )

    token = create_access_token({"sub": user.user_id, "role": user.role, "user_id": user.user_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "role": user.role,
    }


@router.get("/", response_model=List[UserOut])
def get_users(role: Optional[UserRole] = None, db: Session = Depends(get_db)):
    if role:
        users = db.query(User).filter(User.role == role).all()
    else:
        users = db.query(User).all()
    return users

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/internal-only", response_model=UserOut)
def admin_only(current_user: User = Depends(require_role(UserRole.internal))):
    return current_user