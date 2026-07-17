from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import PasswordResetToken, User
from schemas import UserCreate, UserOut, ForgotPasswordRequest, ResetPasswordRequest, EmailCheckRequest
from auth import generate_reset_token, hash_password

from datetime import datetime, timedelta
from jose import jwt, JWTError

from email_utils import send_reset_email
from auth import hash_password, verify_password, create_access_token, Token_expire,  Secret_Key, Algorithm

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut) #endpoint
async def register(user: UserCreate, db : AsyncSession = Depends(get_db)): # gets fresh session
    result = await db.execute(select(User).where(User.email== user.email))  #here code runs agaisnt the datbase  # ask sir about dependdecny injection 
    exisitng_user = result.scalar_one_or_none()
    
    if exisitng_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, hashed_password= hashed_pw)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login")
async def login(user_credential: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User). where(User.email== user_credential.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_credential.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token_expire = timedelta(minutes=Token_expire)
    access_token = create_access_token( data= {"sub": user.email}, expires_delta=access_token_expire)  # here we are embedding user email to the jwt token 
    
    return {"access_token": access_token, "token_type": "bearer"} # shape for OAuth2 standard response. 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, Secret_Key, algorithms=[Algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if user:
        user_email = user.email  # grab it now, while the object is still fresh
        user_id = user.id

        token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(minutes=30)

        reset_entry = PasswordResetToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            used=False
        )
        db.add(reset_entry)
        await db.commit()

        send_reset_email(user_email, token)  # use the saved variable, not user.email

    return {"message": "If that email exists, a reset link has been sent."}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):    
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token == request.token))
    reset_entry = result.scalar_one_or_none()

    if not reset_entry or reset_entry.used or reset_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.id == reset_entry.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(request.new_password)
    reset_entry.used = True

    await db.commit()

    return {"message": "Password has been reset successfully."}


@router.post("/check-email")
async def check_email(request: EmailCheckRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    return {"available": user is None}
