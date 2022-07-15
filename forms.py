from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class HomeForm(FlaskForm):
    sign_in = SubmitField("Sign In")
    sign_up = SubmitField("Sign Up")

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Log In')


class ResearchForm(FlaskForm):
    city_name = StringField('City',validators = [DataRequired()])
    distance = StringField('Distance')
    activity = StringField('Activity')
    condition = StringField('Do you require any accommodations: ')
    submit = SubmitField('Search')
