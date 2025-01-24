from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import datetime
import uuid

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Todo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    date = datetime.date.today()
    title = f"My todo-list {date}"
    all_todos = db.session.execute(db.select(Todo).order_by(Todo.id)).scalars().all()
    all_todos = [todo.to_dict() for todo in all_todos]
    completed_todos = []
    uncompleted_todos = []
    for todo in all_todos:
        if todo["completed"]:
            completed_todos.append(todo)
        else:
            uncompleted_todos.append(todo)
    return render_template('home.html', title=title, completed_todos=completed_todos,
                           uncompleted_todos=uncompleted_todos)


@app.route('/submit', methods=['POST'])
def submit():
    task = request.form.get('new-task')
    todos = db.session.execute(db.select(Todo).where(Todo.name == task)).scalars().all()
    if todos:
        return redirect(url_for('home'))
    else:
        new_todo = Todo(uuid=str(uuid.uuid1()), name=task, date="", completed=False)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/delete/<item>', methods=['GET'])
def delete(item):
    item = item.replace("%", " ")
    todos = db.session.execute(db.select(Todo).where(Todo.name == item)).scalars().all()
    if todos:
        db.session.delete(todos[0])
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/setdate/<item>', methods=['GET'])
def setdate(item):
    todos = db.session.execute(db.select(Todo).where(Todo.name == item)).scalars().all()
    if todos:
        todos[0].date = request.args.get("date")
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/markcomplete/<item>', methods=['GET'])
def markcomplete(item):
    todos = db.session.execute(db.select(Todo).where(Todo.name == item)).scalars().all()
    if todos:
        todos[0].completed = True
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
