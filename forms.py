from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('email', validators=[DataRequired(), Email()])
    contact = StringField('contact', validators=[DataRequired(), Length(min=10, max=20)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('i am a', choices=[('user', 'user (trekker)'), ('staff', 'trek staff')])
    submit = SubmitField('register')

class LoginForm(FlaskForm):
    username = StringField('username / email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    role = SelectField('login as', choices=[('user', 'user (trekker)'), ('staff', 'trek staff'), ('admin', 'admin')])
    submit = SubmitField('login')