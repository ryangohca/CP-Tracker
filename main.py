import json
import hashlib # as for now

import flask
from flask import render_template, request, redirect, url_for
from wtforms import Form, StringField, PasswordField, validators

def userNotExist(form, field):
    data = field.data.strip()
    with open("static/passwords.json") as f:
        userDict = json.load(f)
        if data in userDict:
            raise validators.ValidationError("Username already exists.") 

class RegistrationForm(Form):
    username = StringField('Username:', [validators.DataRequired(), validators.Length(min=4, max=25), userNotExist])
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

@app.route("/login", methods=["POST"])
def login():
    pass

@app.route("/success", methods=["GET", "POST"])
def success():
    return render_template("success.html")

@app.route("/", methods=["GET", "POST"])
def signUp():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        with open("static/passwords.json") as f:
            userDict = json.load(f)
            userDict[form.username.data.strip()] = {
                "email": form.email.data,
                "password": hashlib.sha512(bytes(form.password.data, encoding='utf8')).hexdigest()
            }
        with open("static/passwords.json", "w") as f:
            json.dump(userDict, f)
        return redirect(url_for("success"))
    return render_template('index.html', signupForm=form, loginForm=LoginForm())

app.run(host="0.0.0.0", port=8080, debug=True)