
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, Field
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import jwt


# ==========================================
# 1. FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Personal Task Tracker API",
    description="Register, Login and Manage Your Tasks",
    version="1.0.0"
)


# ==========================================
# 2. DATABASE CONFIGURATION
# ==========================================

DATABASE_URL = "sqlite:///./task_tracker_api.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# 3. SECURITY CONFIGURATION
# ==========================================

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)


def create_access_token(data):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================================
# 4. DATABASE MODELS
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(300), default="")
    priority = Column(String(20), default="Medium")
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )


Base.metadata.create_all(bind=engine)


# ==========================================
# 5. PYDANTIC SCHEMAS
# ==========================================

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=300)
    priority: str = "Medium"


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=300)
    priority: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# 6. CURRENT USER AUTHENTICATION
# ==========================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise credentials_exception

    return user


# ==========================================
# 7. HOME
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Welcome to Personal Task Tracker API",
        "docs": "/docs"
    }


# ==========================================
# 8. REGISTER
# ==========================================

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    username = user.username.strip().lower()
    email = user.email.strip().lower()

    if not username or not email or "@" not in email:
        raise HTTPException(
            status_code=400,
            detail="Enter valid username and email"
        )

    existing = db.query(User).filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    new_user = User(
        username=username,
        email=email,
        password=get_password_hash(user.password)
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Registration failed"
        )

    return new_user


# ==========================================
# 9. LOGIN
# ==========================================

@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    username = form_data.username.strip().lower()

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        {"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ==========================================
# 10. MY PROFILE
# ==========================================

@app.get("/users/me", response_model=UserResponse)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# ==========================================
# 11. ADD TASK
# ==========================================

@app.post("/tasks", response_model=TaskResponse, status_code=201)
def add_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Task title cannot be empty"
        )

    if task.priority not in ["High", "Medium", "Low"]:
        raise HTTPException(
            status_code=400,
            detail="Priority must be High, Medium or Low"
        )

    new_task = Task(
        title=task.title.strip(),
        description=task.description.strip(),
        priority=task.priority,
        user_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# ==========================================
# 12. VIEW ALL TASKS
# ==========================================

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(Task).filter(
        Task.user_id == current_user.id
    ).order_by(Task.created_at.desc()).all()


# ==========================================
# 13. VIEW SINGLE TASK
# ==========================================

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# ==========================================
# 14. UPDATE TASK
# ==========================================

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    data = task_data.model_dump(exclude_unset=True)

    for key, value in data.items():

        if key == "title" and value is not None:
            value = value.strip()

            if not value:
                raise HTTPException(
                    status_code=400,
                    detail="Title cannot be empty"
                )

        if key == "description" and value is not None:
            value = value.strip()

        if key == "priority" and value is not None:
            if value not in ["High", "Medium", "Low"]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid priority"
                )

        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


# ==========================================
# 15. COMPLETE / PENDING TASK
# ==========================================

@app.patch("/tasks/{task_id}/complete")
def toggle_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.is_completed = not task.is_completed

    db.commit()

    return {
        "message": "Task status updated",
        "task_id": task.id,
        "is_completed": task.is_completed
    }


# ==========================================
# 16. DELETE TASK
# ==========================================

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }


# ==========================================
# 17. LOGOUT
# ==========================================

@app.post("/logout")
def logout():
    return {
        "message": "Logout successful. Clear your token in Swagger."
    }
