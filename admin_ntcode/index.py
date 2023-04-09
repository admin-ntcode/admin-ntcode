import json

from flask import Flask, make_response, render_template, request, session, redirect, url_for

from pymongo import *

import urllib.parse
app = Flask(__name__)
app.secret_key = 'bossBigBoss'
client = MongoClient('mongodb+srv://akshit:akshit@cluster0.dcipu28.mongodb.net/?retryWrites=true&w=majority')
db = client['userdata']
user_collection = db['userlist']
usercode_collection = db['usercode']


@app.route('/')
@app.route('/home')
@app.route('/home/')
def index():
    #print(user_collection.find({}))
    """for x in usercode_collection.find({}):
        if x['name'].startswith('klcp[k\'p;c'):
            usercode_collection.delete_one({'name': x['name']})"""
    if 'username' in session:
        return render_template('index.html')

    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly

    return render_template('404.html'), 404


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('form'))

    if request.method == 'POST':

        # Get the user's input

        username = request.form['username']

        password = request.form['password']

        # Check if the user exists in the database

        user = user_collection.find_one({'username': username, 'password': password})

        if user:

            session['username'] = username

            return redirect('/')

        else:

            return render_template('alert.html', title="Error!", text='Invalid username or password', icon="error",
                                   red="form")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if "username" in session:
        return redirect(url_for('form'))

    if request.method == 'POST':

        # Get the user's input

        name = request.form['name']

        username = request.form['username']

        bio = request.form['bio']

        password = request.form['password']

        password2 = request.form['password2']

        # Check if the passwords match

        if password != password2:
            return render_template('alert.html', title="Error!", text='Passwords do not match', icon="error",
                                   red="login")

        # Check if the user already exists

        existing_user = user_collection.find_one({'username': username})

        if existing_user:
            return render_template('alert.html', title="Error!", text='Username already exists', icon="error",
                                   red="login")

        # Insert the new user into the database

        user_collection.insert_one({'name': name, 'username': username, 'bio': bio, 'password': password})

        # Log the user in

        session['username'] = username

        return redirect('/')

    return render_template('register.html')

@app.route('/form', methods=['GET', 'POST'])
@app.route('/form/', methods=['GET', 'POST'])
def form():
    if not "username" in session:
        return render_template('alert.html', title="Fatal!", text="User not logged in!", icon="error", red='login')

    if request.method == 'POST':


        ######################################################################################################
        # Get the user's input
        # Try to extract the first name from the "name" field of the form data submitted with the request
        try:
            name = request.form['name'].split(' ')[0]  # Split the name by spaces and take the first element
            name = urllib.parse.unquote(name.strip()).strip()  # Unquote and strip any whitespace from the name
        except KeyError as e:
            # If the "name" field is not found in the form data, raise a KeyError and print an error message
            print("name not found in POST method to /form")
            return str(e)+"\n KeyError in 'name' "
        except:
            return "Error in 'name' in /form/ POST "
        #######################################################################################################
        try:
            sdes=request.form['single'] #single line description
        except:
            return "Error in sdes in /form/ POST \n"
        ######################################################################################################
        # Try to modify the "description" field of the form data using a module called "md"
        try:
            import md
            print(request.form['description'])
            description =request.form['description'].replace('\\n', '\n')
            print(description)
            #des_raw=request.form['description'] 
            # not needed anymore
        except KeyError as e:
            # If the "description" field is not found in the form data, raise a KeyError and print an error message
            print("description not found in POST method to /form")
            return str(e)+" \n error in description (key error) in /form/ POST "
        except:
            return "Error in description in /form/ POST \n"
        ######################################################################################################
        # Try to extract the "code" field from the form data submitted with the request
        code = "//written on ntcode.ml"
        try:
            code = request.form['javacode']
        except:
            return " Unreachable"
        ######################################################################################################
        
        # Check if the user is logged in

        if 'username' not in session:
            return 'You must be logged in to submit code'

        # Insert the new code into the database

        author = session['username']

        if usercode_collection.find_one({"name": name}):
            return render_template('alert.html', title="Error!", text="Code Exists", icon="error", red="form")

        usercode_collection.insert_one(
            {'name': name, 'description': description,"sdes":sdes, 'code': code.replace('\\n', '\n'), 'author': author})
        
        return render_template('alert.html', title="Done!", text="Successfully Appended the code", icon="success",
                               red='form')

    return render_template('form.html')


@app.route('/form/<name>', methods=['POST', 'GET'])
@app.route('/form/<name>/', methods=['POST', 'GET'])
def editEntry(name):
    if request.method == 'POST':
        data_temp = usercode_collection.find_one({"name": name})

        sdes=request.form['single']

        description = request.form['description']

        code = request.form['javacode']

        usercode_collection.update_one({"name": name}, {"$set": {"code": code}})

        usercode_collection.update_one({"name": name}, {"$set": {"sdes": sdes}})

        usercode_collection.update_one({"name": name}, {"$set": {"description": description}})

        return render_template('alert.html', title="Done!", text="Successfully Edited the code", icon="success",
                               red='form')

    if not "username" in session:
        return render_template('alert.html', title="Fatal!", text="User not logged in!", icon="error", red='login')

    data = usercode_collection.find_one({"name": name})

    if data:

        if data['author'] == session['username']:

            return render_template('edit.html', name=name, code=data['code'], des=data['description'],sdes = data['sdes'])

        else:

            return render_template('alert.html', title="Fatal!", text="U must login with Your account to edit .",
                                   icon="error", red='profile')

    else:

        return render_template('alert.html', title="Fatal!", text="Could not find code", icon="error", red='list')

@app.route('/list')
@app.route('/list/')
def list():
    return render_template('list.html', entries=usercode_collection.find())


@app.route('/logout')
@app.route('/logout/')
def logout():
    session.pop('username', None)

    return redirect('/')

@app.route("/profile", methods=["GET", "POST"])
@app.route("/profile/", methods=["GET", "POST"])
def profile():
    if request.method == "POST":

        name = request.form["name"]

        bio = request.form["bio"]

        username = session["username"]

        user_collection.update_one({"username": username}, {"$set": {"name": name, "bio": bio}})

        return redirect("/profile")

    elif "username" in session:

        user = user_collection.find_one({"username": session["username"]})

        return render_template("profile.html", name=user["name"], username=user["username"], bio=user["bio"])

    else:

        return redirect("/login")


@app.route("/delete/<name>", methods=["GET", "POST"])
@app.route("/delete/<name>/", methods=["GET", "POST"])
def delete(name):
    # Delete the entry with the given id

    result = usercode_collection.delete_one({"name": name})

    # Check if the entry was successfully deleted

    if result.deleted_count == 1:

        # Redirect to the list page
        return render_template('alert.html', title="Done!", text="Successfully Deleted the entry", icon="success",
                               red='list')

    else:

        # Return an error message if the entry was not deleted

        return render_template('alert.html', title="Error!", text="Could not delete the entry", icon="error",
                               red='list')


@app.route('/download/<username>', methods=['GET'])
@app.route('/download/<username>/', methods=['GET'])
def download_codes(username):
    # get all codes by the user from the database

    user_codes = usercode_collection.find({'author': username})

    # create a list of code dictionaries

    code_list = []

    for code in user_codes:
        code_dict = {

            'title': code['name'],

            'language': code['description'],

            'content': code['code']

        }

        code_list.append(code_dict)

    # convert the list to JSON format

    json_data = json.dumps(code_list, indent=4)

    # create a response with the JSON data and appropriate headers

    response = make_response(json_data)

    response.headers['Content-Disposition'] = 'attachment; filename="{}-codes.json"'.format(username)

    return response

@app.route('/test')
def test():
    import md
    return md.mdfy(usercode_collection.find({"name":"Test"})[0]['description'])


@app.route('/get/code/<name>/')
@app.route('/get/code/<name>')
def getcode(name):
    return usercode_collection.find({"name":name})[0]['code']


@app.route('/get/description/<name>')
def getdescription(name):
    import md
    return md.mdfy(usercode_collection.find({"name":name})[0]['description'])


@app.route('/get/sdes/<name>/')
@app.route('/get/sdes/<name>')
def sdes(name):
    return usercode_collection.find({"name":name})[0]['sdes']
@app.route('/download/code/<name>', methods=['GET'])
def download_codes_user(name):
    # get all codes by the user from the database

    user_codes = usercode_collection.find({'name': name})

    # create a list of code dictionaries

    code_list = []

    for code in user_codes:
        code_dict = {

            'title': code['name'],

            'language': code['description'],

            'content': str(code['code'])

        }

        code_list.append(code_dict)

    # convert the list to JSON format

    json_data = json.dumps(code_list, indent=4)

    # create a response with the JSON data and appropriate headers

    response = make_response(json_data)

    response.headers['Content-Disposition'] = 'attachment; filename="{}-codes.json"'.format(name)

    return response
@app.route('/change/password',methods=['POST','GET'])
@app.route('/change/password/',methods=['POST','GET'])
def chpass():
    if not "username" in session :
        return render_template('alert.html', title="Fatal!", text="User not logged in!", icon="error", red='')
    if request.method == 'POST':
        oldpass=request.form['old_password']
        if oldpass == user_collection.find_one({'username':session["username"]})['password']:
            if request.form['new_password'] == request.form['confirm_password']:
                user_collection.update_one({"username": session['username']}, {"$set": {"password": request.form['new_password']}})
                return render_template('alert.html', title="Done", text="Password Changed Successfully", icon="success", red='profile')
            else:
                return render_template('alert.html', title="Fatal!", text="Passwords do not match", icon="error", red='change/password/')
        else:
                return render_template('alert.html', title="Fatal!", text="oLD pass is wrong", icon="error", red='change/password/')
    return render_template('chpass.html')
    return 'Gotch u'


#app.run(port=8000, debug=True)
