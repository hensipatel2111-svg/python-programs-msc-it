from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone


app = FastAPI(title="JWT Authentication API")


# =========================
# JWT CONFIGURATION
# =========================

SECRET_KEY = "my-super-secret-key-for-jwt-authentication-2026"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# =========================
# FAKE DATABASE
# =========================

users_db = {}


# =========================
# PYDANTIC MODELS
# =========================

class UserSignup(BaseModel):
    username: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    username: str
    password: str


# =========================
# REGISTER API
# =========================

@app.post("/register")
def register(user: UserSignup):

    if user.username in users_db:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    users_db[user.username] = {
        "username": user.username,
        "password": user.password,
        "full_name": user.full_name
    }

    print("User registered:", user.username)

    return {
        "message": "User registered successfully",
        "username": user.username
    }


# =========================
# LOGIN API
# =========================

@app.post("/login")
def login(user: UserLogin):

    db_user = users_db.get(user.username)

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if user.password != db_user["password"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    print("User logged in:", user.username)

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user.username,
        "name": db_user["full_name"],
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    print("JWT token generated for:", user.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =========================
# GET CURRENT USER
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = users_db.get(username)

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# =========================
# PROTECTED PROFILE API
# =========================

@app.get("/profile")
def profile(
    current_user: dict = Depends(get_current_user)
):

    print("Profile accessed by:", current_user["username"])

    return {
        "message": "Authentication successful",
        "username": current_user["username"],
        "full_name": current_user["full_name"]
    }