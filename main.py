from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CONFIGURE TABLES
class Todo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="todos")
    def to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    todos = relationship('Todo', back_populates='user')


with app.app_context():
    db.create_all()


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash("You've already signed up with that email. Log in instead!")
            return redirect(url_for("login"))

        hashed_and_salted_pw = get_hashed_and_salted_password(password)
        new_user = User(name=name, email=email, password=hashed_and_salted_pw)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("todo"))
    return render_template("register.html")


def get_hashed_and_salted_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            flash("This email does not exist, please try again.")
            return redirect(url_for("login"))
        elif check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("todo"))
        else:
            flash("Password incorrect, please try again.")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template("home.html")


@login_required
@app.route('/todo')
def todo():
    date = datetime.date.today()
    title = f"My todo list {date}"
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    all_todos = [x.to_dict() for x in todos]
    completed_todos = []
    uncompleted_todos = []
    for x in all_todos:
        if x["completed"]:
            completed_todos.append(x)
        else:
            uncompleted_todos.append(x)
    return render_template('todo.html', title=title, completed_todos=completed_todos,
                           uncompleted_todos=uncompleted_todos)


@login_required
@app.route('/submit', methods=['POST'])
def submit():
    task = request.form.get('new-task')
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    duplicate = list(filter(lambda x: x.name == task, todos))
    if duplicate:
        return redirect(url_for('todo'))
    else:
        new_todo = Todo(uuid=str(uuid.uuid1()), name=task, date="", completed=False, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('todo'))


@login_required
@app.route('/delete/<item>', methods=['GET'])
def delete(item):
    item = item.replace("%", " ")
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    todos = list(filter(lambda x: x.name == item, todos))

    if todos:
        db.session.delete(todos[0])
        db.session.commit()
    return redirect(url_for('todo'))


@login_required
@app.route('/setdate/<item>', methods=['GET'])
def setdate(item):
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    todos = list(filter(lambda x: x.name == item, todos))
    if todos:
        todos[0].date = request.args.get("date")
        db.session.commit()
    return redirect(url_for('todo'))


@login_required
@app.route('/markcomplete/<item>', methods=['GET'])
def markcomplete(item):
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    todos = list(filter(lambda x: x.name == item, todos))
    if todos:
        todos[0].completed = True
        db.session.commit()
    return redirect(url_for('todo'))


if __name__ == "__main__":
    app.run(debug=True, port=5002)
