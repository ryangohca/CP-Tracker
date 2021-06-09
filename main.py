import flask
from flask import render_template, request
from wtforms import Form, StringField, PasswordField, validators

class RegistrationForm(Form):
    username = StringField('Username:', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = StringField('Email Address:', [validators.Length(min=6, max=35)])
    password = PasswordField('Password:', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password:')

class LoginForm(Form):
    username = StringField('Username:', [validators.DataRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password:', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])

app = flask.Flask(__name__)

@app.route("/")
def root():
    signupForm = RegistrationForm()
    loginForm = LoginForm()
    return render_template("index.html", signupForm=signupForm, loginForm=loginForm)

@app.route("/login")
def login():
    pass

@app.route("/signup")
def signUp():
    pass
app.run(host="0.0.0.0", port=8080, debug=True)