from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean, select
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
    # check: Mapped[int] = mapped_column(Boolean, nullable=False)

    user_task_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    user_task = relationship('User', back_populates="task")

with app.app_context():
    db.create_all()

# Home route
@app.route('/', methods=["GET"])
def home():
    if current_user.is_authenticated:
        return redirect(url_for("home_user"))
    return render_template("index.html")

# Home route for user logged in
@app.route('/user/me', methods=["GET", "POST"])
@login_required
def home_user():
    stmt = db.session.scalars(select(Todo).where(Todo.user_task_id==current_user.id).order_by(Todo.priority))
    tasks = stmt.all()
    form = TodoForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to be logged in.")
            return redirect(url_for("login"))
        
        new_task = Todo(
            text = form.text.data,
            date = date.today().strftime("%B %d, %Y"),
            priority = form.priority.data,
            user_task = current_user
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home_user'))
    return render_template("index.html", tasks=tasks, form=form)

# Edit route
@app.route('/task/<int:task_id>/edit', methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = db.get_or_404(Todo, task_id)
    if task.user_task_id!=current_user.id:
        return redirect(url_for("home_user"))
    
    edit_form = TodoForm(
        text = task.text,
        priority = task.priority
    )

    if edit_form.validate_on_submit():
        task.text = edit_form.text.data
        task.priority = edit_form.priority.data
        db.session.commit()
        return redirect(url_for("home_user"))
    
    
    return render_template("edit_task.html", form=edit_form, task=task)

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
        return redirect(url_for('home_user'))
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
            return redirect(url_for('home_user'))
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