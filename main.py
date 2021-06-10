import json
import hashlib # as for now

import flask
from flask import render_template, request, redirect, url_for, abort
from wtforms import Form, StringField, PasswordField, validators

loginUser = None  #Is there a better way?

def userNotExist(form, field):
    username = field.data.strip()
    with open("static/passwords.json") as f:
        userDict = json.load(f)
        if username in userDict:
            raise validators.ValidationError("Username already exists.")

def userExist(form, field):
    username = field.data.strip()
    with open("static/passwords.json") as f:
        userDict = json.load(f)
        if username not in userDict:
            raise validators.ValidationError("Username does not exist in server.")

def passwordMatch(form, field):
    attemptedHashedPassword = hashlib.sha512(bytes(field.data.strip(), encoding='utf8')).hexdigest()
    with open("static/passwords.json") as f:
        userDict = json.load(f)
        if form.username.data.strip() in userDict:
            actualHashedPassword = userDict[form.username.data.strip()]['password']
        else:
            return
    if attemptedHashedPassword != actualHashedPassword:
        raise validators.ValidationError("Password is incorrect.")
    
class RegistrationForm(Form):
    username = StringField('Username:', [validators.DataRequired(), validators.Length(min=4, max=25), userNotExist])
    email = StringField('Email Address:', [validators.Length(min=6, max=35)])
    password = PasswordField('Password:', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password:')

class LoginForm(Form):
    username = StringField('Username:', [validators.DataRequired(), userExist])
    password = PasswordField('Password:', [
        validators.DataRequired(),
        passwordMatch
    ])

app = flask.Flask(__name__)

@app.route("/")
def root():
    signupForm = RegistrationForm()
    loginForm = LoginForm()
    return render_template("index.html", signupForm=signupForm, loginForm=loginForm)

@app.route("/login", methods=["POST"])
def login():
    global loginUser
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        loginUser = form.username.data.strip()
        return redirect(url_for("success"))
    return render_template('index.html', signupForm=RegistrationForm(), loginForm=form)

@app.route("/main", methods=["GET", "POST"])
def success():
    if loginUser is None:
        return abort(503, "Access Denied")
    #TODO: notify user login successful
    return render_template("success.html")

@app.route("/logout")
def logout():
    global loginUser
    loginUser = None
    print(loginUser)
    # TODO: notify user logout successful
    return redirect(url_for('root'))

@app.route("/", methods=["GET", "POST"])
def signUp():
    global loginUser 
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
        loginUser = form.username.data.strip()
        return redirect(url_for("success"))
    return render_template('index.html', signupForm=form, loginForm=LoginForm())

app.run(host="0.0.0.0", port=8080, debug=True)