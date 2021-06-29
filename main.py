import json
import hashlib # as for now
import re
from datetime import date, datetime

import flask
from flask import render_template, request, redirect, url_for, abort
from wtforms import Form, StringField, PasswordField, validators

loginUser = None  #Stores current username that is logged in, or none if no user is logged in.
PASSWORD_FILE = "data/passwords.json"
COLLECTIONS_FILE = "data/collections.json"
IDNAME_FILE = "data/idNames.json"
PUBLIC_COLLECTIONS_FILE = "data/public.json"
ALL_PROBLEM_VERDICTS = ["Unattempted", "Wrong Answer", "Accepted", "Time Limit Exceeded", "Memory Limit Exceeded", "Runtime Error", "Theory Solved", "Query Limit Exceeded", "Presentation Error"]

def userNotExist(form, field):
    """Checks if username exists in the server. Throws ValidationError if username does not exist."""
    username = field.data.strip()
    with open(PASSWORD_FILE) as f:
        userDict = json.load(f)
        if username in userDict:
            raise validators.ValidationError("Username already exists.")

def userExist(form, field):
    """Checks if username does not exist in our server. If it does exist, throw ValidationError."""
    username = field.data.strip()
    with open(PASSWORD_FILE) as f:
        userDict = json.load(f)
        if username not in userDict:
            raise validators.ValidationError("Username does not exist in server.")

def passwordMatch(form, field):
    """Checks if password of the user matches the one stored in the server. Throws ValidationError if passwords do not match."""
    # We do not strip leading / ending spaces, it could be deliberate as a password.
    attemptedHashedPassword = hashlib.sha512(bytes(field.data, encoding='utf8')).hexdigest()
    with open(PASSWORD_FILE) as f:
        userDict = json.load(f)
        # wt-forms evaulates all validators before submitting the form, even if the previous validator fails
        # so we still have to check whether the username is in the database here to avoid a KeyError
        if form.username.data.strip() in userDict:
            actualHashedPassword = userDict[form.username.data.strip()]['password']
        else:
            # if username is not valid, suppress this validator. There is no reason to say it twice, for it would
            # be handled by the validator specific to username.
            # Also, we suppress so that we do not show "Password is incorrect" which is completely absurd in this case. 
            return
    if attemptedHashedPassword != actualHashedPassword:
        raise validators.ValidationError("Password is incorrect.")
    
class RegistrationForm(Form):
    username = StringField('Username:', [validators.DataRequired(), validators.Length(min=4, max=25), userNotExist], id="newUsername")
    email = StringField('Email Address:', [validators.Length(min=6, max=35)])
    password = PasswordField('Password:', [validators.DataRequired()], id="newPassword")
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
    """If login in successful, redirect users to the home page; if not, redirect them back to the login page and shows them the form errors."""
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
    with open(COLLECTIONS_FILE) as f:
        myCollections = json.load(f)[loginUser]["collections"]
    with open(PUBLIC_COLLECTIONS_FILE) as f:
        publicCollections = json.load(f)
    orderKey = sorted(myCollections, key=lambda x: datetime.strptime(myCollections[x]["createdDate"], "%d/%m/%Y"))
    publicOrderKey = sorted(publicCollections, key=lambda x: datetime.strptime(publicCollections[x]["createdDate"], "%d/%m/%Y"), reverse=True)
    suggestedIDs = [reformID(collectionId) for collectionId in publicOrderKey]
    if 'failure' in request.args:
        return render_template("homePage.html",
                                failure=request.args['failure'],
                                myCollections=myCollections,
                                orderKey=orderKey,
                                publicCollections=publicCollections,
                                publicOrderKey=publicOrderKey,
                                suggestedIDs=suggestedIDs,
                                allVerdicts=ALL_PROBLEM_VERDICTS)
    if 'warning' in request.args:
        return render_template("homePage.html",
                                warning=request.args['warning'],
                                myCollections=myCollections,
                                orderKey=orderKey,
                                publicCollections=publicCollections,
                                publicOrderKey=publicOrderKey,
                                suggestedIDs=suggestedIDs,
                                allVerdicts=ALL_PROBLEM_VERDICTS)
    if 'success' in request.args:
         return render_template("homePage.html",
                                success=request.args['success'],
                                myCollections=myCollections,
                                orderKey=orderKey,
                                publicCollections=publicCollections,
                                publicOrderKey=publicOrderKey,
                                suggestedIDs=suggestedIDs,
                                allVerdicts=ALL_PROBLEM_VERDICTS)
    return render_template("homePage.html",
                            myCollections=myCollections,
                            orderKey=orderKey,
                            publicCollections=publicCollections,
                            publicOrderKey=publicOrderKey,
                            suggestedIDs=suggestedIDs,
                            allVerdicts=ALL_PROBLEM_VERDICTS)

@app.route("/logout")
def logout():
    global loginUser
    loginUser = None
    print(loginUser)
    # TODO: notify user logout successful
    return redirect(url_for('root'))

@app.route("/", methods=["GET", "POST"])
def signUp():
    """If successful, auto log the user in. If not, redirect them back to the login page and show all the form errors."""
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
        return redirect(url_for("success", success="Login is successful!"))
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
    """Modify `usedID` such that the returned id is unique to the ids stored in the server.
    
    The `usedID` is modified as follows:
    1. remove any trailing numbers. Let the resulting string be s.
    2. Brute force all the possible integers starting from 1. 
       Returns the smallest integer x such that s + str(x) is an unused id.
    """
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
    
    # Get all current data.
    with open(COLLECTIONS_FILE) as f:
        allUsersCollections = json.load(f)

    userCollectionIDInput = request.form["collectionID"]
    collectionID = userCollectionIDInput
    warning = ""

    if request.form['idPrefilled'] == "false": # if this is false, it means that id can be changed -> new collection
        if usedID(userCollectionIDInput):
            # changes id by adding a number behind it to make it unique.
            collectionID = reformID(userCollectionIDInput)  
            warning = f"Collection ID '{userCollectionIDInput}' has been renamed to '{collectionID}' as it is already in use."
        allUsersCollections[loginUser]['collections'][collectionID] = {}

    currCollection = {}
    currCollection['title'] = request.form['collectionTitle']
    currCollection['id'] = collectionID
    currCollection['description'] = request.form['description']
    currCollection['shortDescription'] = currCollection['description'].split("\r\n")[0] # we only consider the very first line for short descriptions
    if len(currCollection['shortDescription']) > 147: # must be at most 150 characters including the ellipsis
        currCollection['shortDescription'] = currCollection['shortDescription'][:147] + "..."
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
        # Why url but not name? There could be 2 problems with the same name, 
        # but unlikely to have 2 different problems to have the same url.
        # So url is a better 'id'.
        prevProblems = {problem['url']: problem for problem in allUsersCollections[loginUser]['collections'][collectionID]['problems']}
    else:
        prevProblems = {}
    if 'createdDate' in allUsersCollections[loginUser]['collections'][collectionID]:
        currCollection['createdDate'] = allUsersCollections[loginUser]['collections'][collectionID]['createdDate']
    else:
        currCollection['createdDate'] = date.today().strftime("%d/%m/%Y")
    regex = re.compile("^(.*?)(\d+)$")
    currCollection['problems'] = []
    solvedProblems = 0
    allUrls = set() # Since url is used as an id, we need to check that all urls in the same collection are unique, or reject input.
    for name in request.form:
        if name.startswith("problemName-"):
            number = regex.match(name).group(2)
            currProblem = {}
            currProblem['name'] = request.form["problemName-" + number]
            currProblem['url'] = request.form["problemUrl-" + number]
            allUrls.add(currProblem['url'])
            currProblem['format'] = request.form["problemFormat-" + number]
            currProblem['solved'] = prevProblems[currProblem['url']]['solved'] if currProblem['url'] in prevProblems else False
            currProblem['status'] = prevProblems[currProblem['url']]['status'] if currProblem['url'] in prevProblems else 'Unattempted'
            currProblem['important'] = prevProblems[currProblem['url']]['important'] if currProblem['url'] in prevProblems else False
            if currProblem['format'] == "IOI":
                currProblem['score'] = prevProblems[currProblem['url']]['score'] if currProblem['url'] in prevProblems else 0
            else:
                currProblem['score'] = 'N.A.'
            if currProblem['solved']:
                solvedProblems += 1
            currCollection['problems'].append(currProblem)
    if len(allUrls) != len(currCollection['problems']): # Oops there's a duplicate url somewhere
        # Very likely the user inputted wrongly, a single url should not point to 2 different problems
        return redirect(url_for('success', failure="There are at least 2 problems with the same url in the collection. Please try again.")) # The function name is called 'success'...

    currCollection['solvedProblems'] = solvedProblems
    currCollection['totalProblems'] = len(currCollection['problems'])
    allUsersCollections[loginUser]['collections'][collectionID] = currCollection

    # Update JSON here, after ensuring that all data is (somewhat) valid.
    if request.form['idPrefilled'] == "false":
        addIDToServer(collectionID)
    with open(COLLECTIONS_FILE, 'w') as f:
        json.dump(allUsersCollections, f, indent=4, sort_keys=True)
    if currCollection['isPublic']:
        uploadToPublic(currCollection, loginUser)
    else:
        deleteFromPublicIfExists(currCollection['id'])
    if warning != '':
        return redirect(url_for('success', warning=warning))
    return redirect(url_for('success', success="Collections Updated!"))
    
@app.route("/updateProblems", methods=["GET", "POST"])
def updateProblems():
    global loginUser
    if loginUser is None:
        return abort(503, "Access Denied")
    collectionID = request.form["collectionID"];
    # The problems did not change in order at all before the form is created or after the form is submitted
    # so we can just safely loop through the problems in 'collectionID'
    with open(COLLECTIONS_FILE) as f:
        allUsersCollections = json.load(f)
    problems = allUsersCollections[loginUser]['collections'][collectionID]['problems']
    numProblemsSolved = 0
    for i in range(len(problems)):
        if problems[i]['format'] == "IOI":
            allUsersCollections[loginUser]['collections'][collectionID]['problems'][i]['score'] = int(request.form['score-' + str(i)])
        else:
            allUsersCollections[loginUser]['collections'][collectionID]['problems'][i]['score'] = request.form['score-' + str(i)]
        allUsersCollections[loginUser]['collections'][collectionID]['problems'][i]['status'] = request.form['problemVerdict-' + str(i)]
        allUsersCollections[loginUser]['collections'][collectionID]['problems'][i]['important'] = request.form['isImportant-' + str(i)] == "True"
        if request.form['problemVerdict-' + str(i)] == "Accepted":
            allUsersCollections[loginUser]['collections'][collectionID]['problems'][i]['solved'] = True
            numProblemsSolved += 1
    allUsersCollections[loginUser]['collections'][collectionID]['solvedProblems'] = numProblemsSolved
    with open(COLLECTIONS_FILE, 'w') as f:
        json.dump(allUsersCollections, f, indent=4, sort_keys=True)
    return redirect(url_for('success', success="Problem(s) statuses saved."))

@app.route("/deleteCollections", methods=["GET", "POST"])
def deleteCollections():
    global loginUser
    if loginUser is None:
        return abort(503, "Access Denied")
    with open(COLLECTIONS_FILE) as f:
        allUsersCollections = json.load(f)
    with open(IDNAME_FILE) as f:
        idNames = json.load(f)
    for collection in request.form:
        deleteFromPublicIfExists(collection)
        del idNames[collection]
        del allUsersCollections[loginUser]['collections'][collection]
    with open(COLLECTIONS_FILE, 'w') as f:
        json.dump(allUsersCollections, f, indent=4, sort_keys=True)
    with open(IDNAME_FILE, 'w') as f:
        json.dump(idNames, f, indent=4, sort_keys=True)
    return redirect(url_for('success', success=f"{len(request.form)} collection(s) deleted successfully."))

@app.route('/checkID')
def checkID():
    with open(IDNAME_FILE) as f:
        allIDs = json.load(f)
    return render_template('idChecker.html', allIDs=allIDs)

def uploadToPublic(collectionData, uploadedBy):
    # This overwrites previous data if id clashes
    with open(PUBLIC_COLLECTIONS_FILE) as f:
        publicCollections = json.load(f)
    dataToUpdate = {}
    dataToUpdate['createdDate'] = collectionData['createdDate']
    dataToUpdate['description'] = collectionData['description']
    dataToUpdate['owner'] = uploadedBy
    dataToUpdate['id'] = collectionData['id']
    dataToUpdate['publishedDate'] = collectionData['publishedDate']
    dataToUpdate['shortDescription'] = collectionData['shortDescription']
    dataToUpdate['title'] = collectionData['title']
    dataToUpdate['problems'] = []
    for problem in collectionData['problems']:
        thisProblem = {}
        thisProblem['format'] = problem['format']
        thisProblem['name'] = problem['name']
        thisProblem['url'] = problem['url']
        dataToUpdate['problems'].append(thisProblem)
    publicCollections[collectionData['id']] = dataToUpdate
    with open(PUBLIC_COLLECTIONS_FILE, 'w') as f:
        json.dump(publicCollections, f, indent=4, sort_keys=True)

def deleteFromPublicIfExists(collectionID):
    with open(PUBLIC_COLLECTIONS_FILE) as f:
        publicCollections = json.load(f)
    if collectionID in publicCollections:
        del publicCollections[collectionID]
        with open(PUBLIC_COLLECTIONS_FILE, 'w') as f:
            json.dump(publicCollections, f, indent=4, sort_keys=True)

@app.route('/clonePublic', methods=["GET", "POST"])
def clonePublic():
    global loginUser
    if loginUser is None:
        return abort(503, "Access Denied")
    newID = request.form['newID']
    warning = ''
    if usedID(newID):
        newID = reformID(newID)
        warning = f"Collection ID '{request.form['newID']}' has been renamed to '{newID}' as it is already in use."
    originalCollectionID = request.form['originalID']
    with open(PUBLIC_COLLECTIONS_FILE) as f:
        # We will modify from the data gotten in PUBLIC_COLLECTIONS_FILE
        clonedCollection = json.load(f)[originalCollectionID]
    del clonedCollection['owner']
    clonedCollection['id'] = newID
    clonedCollection['isPublic'] = False
    clonedCollection['publishedDate'] = None
    clonedCollection['solvedProblems'] = 0
    clonedCollection['totalProblems'] = len(clonedCollection['problems'])
    for i in range(clonedCollection['totalProblems']):
        if clonedCollection['problems'][i]['format'] == "ICPC":
            clonedCollection['problems'][i]['score'] = "N.A."
        else:
            clonedCollection['problems'][i]['score'] = 0
        clonedCollection['problems'][i]['important'] = False
        clonedCollection['problems'][i]['solved'] = False
        clonedCollection['problems'][i]['status'] = "Unattempted"

    with open(COLLECTIONS_FILE) as f:
        allUserCollections = json.load(f)

    allUserCollections[loginUser]['collections'][newID] = clonedCollection

    addIDToServer(newID)
    with open(COLLECTIONS_FILE, 'w') as f:
        json.dump(allUserCollections, f, indent=4, sort_keys=True)
    
    if warning != '':
        return redirect(url_for('success', warning=warning))
    else:
        return redirect(url_for('success', success=f"Public Collection `{clonedCollection['title']}` cloned!"))

app.run(host="0.0.0.0", port=8080, debug=True)
