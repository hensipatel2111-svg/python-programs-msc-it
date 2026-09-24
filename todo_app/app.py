from flask import Flask, render_template, request, redirect
from datetime import datetime

from db_config import db, Todoapp


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ---------------- HOME ----------------

@app.route("/")
def home():

    pending_tasks = Todoapp.query.filter_by(
        is_completed=False
    ).all()

    completed_tasks = Todoapp.query.filter_by(
        is_completed=True
    ).all()

    return render_template(
        "home.html",
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


# ---------------- ADD TASK ----------------

@app.route("/add", methods=["POST"])
def add_task():

    title = request.form.get("title")

    description = request.form.get("description")

    priority = request.form.get("priority")

    due_date = request.form.get("due_date")

    due_date = datetime.strptime(
        due_date,
        "%Y-%m-%d"
    ).date()

    new_task = Todoapp(
        title=title,
        description=description,
        priority=priority,
        is_completed=False,
        due_date=due_date
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect("/")


# ---------------- TOGGLE TASK ----------------

@app.route("/toggle/<int:id>")
def toggle_task(id):

    task = Todoapp.query.get(id)

    if task:

        task.is_completed = not task.is_completed

        db.session.commit()

    return redirect("/")


# ---------------- EDIT PAGE ----------------

@app.route("/edit/<int:id>")
def edit_task(id):

    task = Todoapp.query.get(id)

    return render_template(
        "edit.html",
        task=task
    )


# ---------------- UPDATE TASK ----------------

@app.route("/update/<int:id>", methods=["POST"])
def update_task(id):

    task = Todoapp.query.get(id)

    task.title = request.form.get("title")

    task.description = request.form.get("description")

    task.priority = request.form.get("priority")

    task.due_date = datetime.strptime(
        request.form.get("due_date"),
        "%Y-%m-%d"
    ).date()

    db.session.commit()

    return redirect("/")


# ---------------- DELETE TASK ----------------

@app.route("/delete/<int:id>", methods=["POST"])
def delete_task(id):

    task = Todoapp.query.get(id)

    if task:

        db.session.delete(task)

        db.session.commit()

    return redirect("/")


# ---------------- RUN APP ----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    print("Database created successfully!")

    app.run(
        port=5000,
        debug=True
    )