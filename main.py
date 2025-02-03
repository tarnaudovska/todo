from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, select
from forms import TodoForm, RegisterForm, LoginForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap(app)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', 'sqlite:///todo-list.db')
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# user table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    task = relationship("Todo", back_populates="user_task")

# tasks todo table
class Todo(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str] = mapped_column(String, nullable=True)

    user_task_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    user_task = relationship('User', back_populates="task")

with app.app_context():
    db.create_all()

# Home route
@app.route('/', methods=["GET", "POST"])
def home():
    stmt = db.session.scalars(select(Todo).order_by(Todo.priority))
    tasks = stmt.all()
    form = TodoForm()
    if form.validate_on_submit():
        print("inside form validation")
        new_task = Todo(
            text = form.text.data,
            date = date.today().strftime("%B %d, %Y"),
            priority = form.priority.data,
            user_task = current_user
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("index.html", tasks=tasks, form=form, current_user=current_user)

# Register route
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    print("u are in register form")
    print(form.validate_on_submit())
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already used")
            return redirect(url_for('login'))
        
        new_user = User(
            name = form.name.data,
            email = form.email.data,
            password = generate_password_hash(form.password.data, salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form, current_user=current_user)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password", "error")
    return render_template('login.html', form=form, current_user=current_user)

@app.route('/logout', methods=["GET", "POST"])
def logout():
    logout_user()
    flash("You've been logged out")
    return redirect(url_for('home'))

@app.route('/contact', methods=["GET", "POST"])
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)