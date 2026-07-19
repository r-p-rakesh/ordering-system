from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.auth.models import User
from app.auth.schemas import UserLogin, UserResponse,UserSignup, Token
from app.auth.utils import hash_password,verify_password,create_access_token,get_current_user,security
from app.auth.models import BlacklistedToken
from fastapi.security import HTTPAuthorizationCredentials

router  =APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email==user.email).first()
    if  existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role= user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login",response_model=Token)
def login(credential: UserLogin, db:Session = Depends(get_db)):
    user=db.query(User).filter(User.email==credential.email).first()
    if not user or not verify_password( credential.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token =create_access_token({"user_id":user.id, "role":user.role.value})
    return {"access_token":token}

@router.get("/me",response_model=UserResponse)
def get_me(current_user: User =Depends(get_current_user)):
    return current_user



@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    db.add(BlacklistedToken(token=token))
    db.commit()
    return {"detail": "Successfully logged out"}