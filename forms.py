from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, EmailField, PasswordField, validators, ValidationError, SelectField
from wtforms.validators import DataRequired, URL, InputRequired, EqualTo

# todo form
class TodoForm(FlaskForm):
    text = StringField("Todo Title", validators=[DataRequired()])
    priority = SelectField(u'Programming Language', choices=[('1', 'High'), ('2', 'Medium'), ('3', 'Low')])
    date = date.today().strftime("%B %d, %Y")
    submit = SubmitField('Submit Todo Task')

# register form for new users
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign up")

# login form for existing users
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired("Please enter your email address")])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
