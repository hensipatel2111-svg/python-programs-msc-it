
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="my_task_tracker_secret_key_2026"
)

DATABASE_URL = "sqlite:///./tasks.db"

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


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(300))
    priority = Column(String(20), default="Medium")
    is_completed = Column(Boolean, default=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")

    if not username:
        return RedirectResponse("/login", status_code=303)

    pending_tasks = db.query(Task).filter(
        Task.created_by == username,
        Task.is_completed == False
    ).order_by(Task.created_at.desc()).all()

    completed_tasks = db.query(Task).filter(
        Task.created_by == username,
        Task.is_completed == True
    ).order_by(Task.created_at.desc()).all()

    theme = request.cookies.get("theme", "light")

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "username": username,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "theme": theme
        }
    )


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@app.post("/login")
def login(request: Request, username: str = Form(...)):
    username = username.strip()

    if not username:
        return RedirectResponse("/login", status_code=303)

    request.session["username"] = username

    return RedirectResponse("/", status_code=303)


@app.post("/add")
def add_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    db: Session = Depends(get_db)
):
    username = request.session.get("username")

    if not username:
        return RedirectResponse("/login", status_code=303)

    title = title.strip()
    description = description.strip()

    if not title or len(title) > 150 or len(description) > 300:
        return RedirectResponse("/", status_code=303)

    if priority not in ["High", "Medium", "Low"]:
        priority = "Medium"

    task = Task(
        title=title,
        description=description,
        priority=priority,
        created_by=username
    )

    db.add(task)
    db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/toggle/{id}")
def toggle_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    username = request.session.get("username")

    if not username:
        return RedirectResponse("/login", status_code=303)

    task = db.query(Task).filter(
        Task.id == id,
        Task.created_by == username
    ).first()

    if task:
        task.is_completed = not task.is_completed
        db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/edit/{id}")
def edit_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    username = request.session.get("username")

    if not username:
        return RedirectResponse("/login", status_code=303)

    task = db.query(Task).filter(
        Task.id == id,
        Task.created_by == username
    ).first()

    if not task:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={"task": task, "username": username}
    )


@app.post("/update/{id}")
def update_task(
    id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    db: Session = Depends(get_db)
):
    username = request.session.get("username")

    if not username:
        return RedirectResponse("/login", status_code=303)

    task = db.query(Task).filter(
        Task.id == id,
        Task.created_by == username
    ).first()

    if not task:
        return RedirectResponse("/", status_code=303)

    title = title.strip()
    description = description.strip()

    if not title or len(title) > 150 or len(description) > 300:
        return RedirectResponse(f"/edit/{id}", status_code=303)

    if priority not in ["High", "Medium", "Low"]:
        priority = "Medium"

    task.title = title
    task.description = description
    task.priority = priority

    db.commit()

    return RedirectResponse("/", status_code=303)


@app.post("/delete/{id}")
def delete_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    username = request.session.get("username")

    if not username:
        return RedirectResponse("/login", status_code=303)

    task = db.query(Task).filter(
        Task.id == id,
        Task.created_by == username
    ).first()

    if task:
        db.delete(task)
        db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/set-theme/{theme}")
def set_theme(theme: str, request: Request):
    if not request.session.get("username"):
        return RedirectResponse("/login", status_code=303)

    if theme not in ["light", "dark"]:
        return RedirectResponse("/", status_code=303)

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key="theme",
        value=theme,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        samesite="lax"
    )

    return response


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
