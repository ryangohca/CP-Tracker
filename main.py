import json
import hashlib # as for now
import re
from datetime import date, datetime

import flask
from flask import render_template, request, redirect, url_for, abort
from wtforms import Form, StringField, PasswordField, validators

loginUser = None  #Is there a better way?
PASSWORD_FILE = "data/passwords.json"
COLLECTIONS_FILE = "data/collections.json"
IDNAME_FILE = "data/idNames.json"

def userNotExist(form, field):
    username = field.data.strip()
    with open(PASSWORD_FILE) as f:
        userDict = json.load(f)
        if username in userDict:
            raise validators.ValidationError("Username already exists.")

def userExist(form, field):
    username = field.data.strip()
    with open(PASSWORD_FILE) as f:
        userDict = json.load(f)
        if username not in userDict:
            raise validators.ValidationError("Username does not exist in server.")

def passwordMatch(form, field):
    attemptedHashedPassword = hashlib.sha512(bytes(field.data.strip(), encoding='utf8')).hexdigest()
    with open(PASSWORD_FILE) as f:
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
    password = PasswordField('Password:', [validators.DataRequired()])
    confirm = PasswordField('Confirm Password:', [validators.EqualTo('password', message='Passwords must match')])

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

@app.route("/home", methods=["GET", "POST"])
def success():
    if loginUser is None:
        return abort(503, "Access Denied")
    #TODO: notify user login successful\
    with open(COLLECTIONS_FILE) as f:
        myCollections = json.load(f)[loginUser]["collections"]
    orderKey = sorted(myCollections, key=lambda x: datetime.strptime(myCollections[x]["createdDate"], "%d/%m/%Y"))
    if 'warning' in request.args:
        return render_template("homePage.html", warning=request.args['warning'], myCollections=myCollections, orderKey=orderKey)
    return render_template("homePage.html", myCollections=myCollections, orderKey=orderKey)

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
        with open(PASSWORD_FILE) as f:
            userDict = json.load(f)
            userDict[form.username.data.strip()] = {
                "email": form.email.data,
                "password": hashlib.sha512(bytes(form.password.data, encoding='utf8')).hexdigest()
            }
        with open(PASSWORD_FILE, "w") as f:
            json.dump(userDict, f, indent=4, sort_keys=True)
        loginUser = form.username.data.strip()
        with open(COLLECTIONS_FILE) as f:
            collections = json.load(f)
        collections[loginUser] = {}
        collections[loginUser]['collections'] = {}
        with open(COLLECTIONS_FILE, 'w') as f:
            json.dump(collections, f, indent=4, sort_keys=True)
        return redirect(url_for("success"))
    return render_template('index.html', signupForm=form, loginForm=LoginForm())

def usedID(id):
    """Checks if ID is already used in the server."""
    with open(IDNAME_FILE) as f:
        ids = json.load(f)
        if id in ids:
            return True
        else:
            return False

def reformID(usedID):
    with open(IDNAME_FILE) as f:
        ids = json.load(f)
    regex = re.compile("^(.*?)(\d*)$")
    baseName = regex.match(usedID).group(1)
    curridx = 1 # We do not want a "<name>0"
    while True:
        if baseName + str(curridx) in ids:
            curridx += 1
        else:
            return baseName + str(curridx)

def addIDToServer(collectionID):
    with open(IDNAME_FILE) as f:
        ids = json.load(f)
    ids[collectionID] = None
    with open(IDNAME_FILE, 'w') as f:
        json.dump(ids, f, indent=4, sort_keys=True)

@app.route("/addCollection", methods=["GET", "POST"])
def addCollection():
    global loginUser
    if loginUser is None:
        return abort(503, "Access Denied")
    userCollectionIDInput = request.form["collectionID"]
    collectionID = userCollectionIDInput
    warning = ""
    with open(COLLECTIONS_FILE) as f:
        allUsersCollections = json.load(f)
    if request.form['idPrefilled'] == "false":
        if usedID(userCollectionIDInput):
            collectionID = reformID(userCollectionIDInput)
            warning = f"Collection ID '{userCollectionIDInput}' has been renamed to '{collectionID}' as it is already in use."
        addIDToServer(collectionID)
        allUsersCollections[loginUser]['collections'][collectionID] = {}
    currCollection = {}
    currCollection['title'] = request.form['collectionTitle']
    currCollection['id'] = collectionID
    currCollection['description'] = request.form['description']
    if 'publicCheckbox' in request.form:
        currCollection['isPublic'] = True
        if 'publishedDate' in allUsersCollections[loginUser]['collections'][collectionID] and allUsersCollections[loginUser]['collections'][collectionID]['publishedDate'] is not None:
            currCollection['publishedDate'] = allUsersCollections[loginUser]['collections'][collectionID]['publishedDate']
        else:
            currCollection['publishedDate'] = date.today().strftime("%d/%m/%Y")
    else:
        currCollection['isPublic'] = False
        currCollection["publishedDate"] = None
    if 'problems' in allUsersCollections[loginUser]['collections'][collectionID]:
        prevProblems = {problem['name']: problem for problem in allUsersCollections[loginUser]['collections'][collectionID]['problems']}
    else:
        prevProblems = {}
    if 'createdDate' in allUsersCollections[loginUser]['collections'][collectionID]:
        currCollection['createdDate'] = allUsersCollections[loginUser]['collections'][collectionID]['createdDate']
    else:
        currCollection['createdDate'] = date.today().strftime("%d/%m/%Y")
    regex = re.compile("^(.*)(\d)+$")
    currCollection['problems'] = []
    solvedProblems = 0
    for name in request.form:
        if name.startswith("problemName-"):
            number = regex.match(name).group(2)
            currProblem = {}
            currProblem['name'] = request.form["problemName-" + number]
            currProblem['url'] = request.form["problemUrl-" + number]
            currProblem['format'] = request.form["problemFormat-" + number]
            currProblem['solved'] = prevProblems[currProblem['name']]['solved'] if currProblem['name'] in prevProblems else False
            if currProblem['solved']:
                solvedProblems += 1
            currCollection['problems'].append(currProblem)
    currCollection['solvedProblems'] = solvedProblems
    currCollection['totalProblems'] = len(currCollection['problems'])
    allUsersCollections[loginUser]['collections'][collectionID] = currCollection
    with open(COLLECTIONS_FILE, 'w') as f:
        json.dump(allUsersCollections, f, indent=4, sort_keys=True)
    if warning != '':
        return redirect(url_for('success', warning=warning))
    return redirect(url_for('success'))
    
app.run(host="0.0.0.0", port=8080, debug=True)