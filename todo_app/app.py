from datetime import datetime
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

database_path = Path(__file__).resolve().parent / "todo.db"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{database_path.as_posix()}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Todoapp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), nullable=False, default="")
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    due_date = db.Column(db.Date, nullable=False)


with app.app_context():
    db.create_all()


def read_form_date():
    date_text = request.form.get("due_date", "").strip()

    if not date_text:
        abort(400, description="Please select a due date.")

    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        abort(400, description="Please enter a valid due date.")


def read_priority():
    priority = request.form.get("priority", "Medium")

    if priority not in {"High", "Medium", "Low"}:
        return "Medium"

    return priority


@app.route("/")
def home():
    pending_tasks = (
        Todoapp.query.filter_by(is_completed=False)
        .order_by(Todoapp.due_date.asc(), Todoapp.id.desc())
        .all()
    )

    completed_tasks = (
        Todoapp.query.filter_by(is_completed=True)
        .order_by(Todoapp.due_date.asc(), Todoapp.id.desc())
        .all()
    )

    return render_template(
        "home.html",
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title:
        abort(400, description="Task title is required.")

    if len(title) > 150:
        abort(400, description="Title must be 150 characters or fewer.")

    if len(description) > 300:
        abort(400, description="Description must be 300 characters or fewer.")

    task = Todoapp(
        title=title,
        description=description,
        priority=read_priority(),
        is_completed=False,
        due_date=read_form_date()
    )

    db.session.add(task)
    db.session.commit()

    return redirect(url_for("home"))


@app.route("/toggle/<int:id>")
def toggle(id):
    task = db.get_or_404(Todoapp, id)

    task.is_completed = not task.is_completed

    db.session.commit()

    return redirect(url_for("home"))


@app.route("/edit/<int:id>")
def edit(id):
    task = db.get_or_404(Todoapp, id)

    return render_template("edit.html", task=task)


@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    task = db.get_or_404(Todoapp, id)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title:
        abort(400, description="Task title is required.")

    if len(title) > 150:
        abort(400, description="Title must be 150 characters or fewer.")

    if len(description) > 300:
        abort(400, description="Description must be 300 characters or fewer.")

    task.title = title
    task.description = description
    task.priority = read_priority()
    task.due_date = read_form_date()

    db.session.commit()

    return redirect(url_for("home"))


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    task = db.get_or_404(Todoapp, id)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
