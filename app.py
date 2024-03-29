#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sqlite3
from tempfile import mkdtemp

from flask import flash, Flask, flash, render_template, request, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, \
    generate_password_hash

# Configure application
from helpers import *

app = Flask(__name__)
UPLOAD_FOLDER = 'static/profile_photos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure templates are auto-reloaded

app.config['TEMPLATES_AUTO_RELOAD'] = True


# Ensure responses aren't cached

@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = \
        'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response


# Configure session to use filesystem (instead of signed cookies)

app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Connect to DB

conn = sqlite3.connect('database.db', isolation_level=None, check_same_thread=False)
db = conn.cursor()


@app.route('/')
def index():
    """Show portfolio of stocks"""
    isLogged = session.get('user_name') is not None  # if logged in equals true
    return render_template('index.html', isLogged=isLogged)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Ensure username was submitted
        errors = []
        if not username:
            errors.append("Username is missing")
        if not password:
            errors.append("Password is missing")

        if len(errors) != 0:
            return render_template('signin.html', errors=errors)

        rows = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        session['user_name'] = username
        # Ensure username exists and password is correct

        if rows:
            if not check_password_hash(rows[4], password):
                errors.append("Password is not correct !")
        else:
            errors.append("Username is not correct")

            session['user_name'] = username
        if len(errors) != 0:
            return render_template('signin.html', errors=errors)

        # Redirect user to home page
        id = db.execute("SELECT id from users WHERE username=?", (username,)).fetchone()[0]
        session['user_id'] = id
        return redirect('/')

    else:
        return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Register user"""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confpassword = request.form.get('confpassword')
        email = request.form.get('email')
        photo = request.files.get('profile_photo')

        # Ensure username was submitted
        errors = []

        if not username:
            errors.append("Username is missing")
        if not password:
            errors.append("Password is missing")
        if not confpassword:
            errors.append("Password confirmation is missing")
        if not email:
            errors.append("Email is missing")
        if password != confpassword:
            errors.append("Password and its confirmation are not equal !")

        if len(errors) != 0:
            return render_template('signup.html', errors=errors)

        # profile photo
        if photo:
            photoFileName = username + '.jpg'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photoFileName))
        else:
            photoFileName = 'default.jpg'

        db.execute('INSERT into users(username,email,password,photoType) '
                   'VALUES (?,?,?,?)'
                   , (username, email, generate_password_hash(password), photoFileName))

        id = db.execute('SELECT id from users where username=?', (username,)).fetchone()[0]
        session['user_id'] = id

        return redirect(url_for('signup2'))
    else:
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template('signup.html')


@app.route('/signup2', methods=['GET', 'POST'])
def signup2():
    """Register user"""

    if request.method == 'POST':
        name = request.form.get('fullname')
        number = request.form.get('number')
        interests = request.form.get('interests')
        id = session['user_id']

        # Ensure username was submitted
        errors = []

        if not name:
            errors.append("Name is missing")
        if not number:
            errors.append("Number is missing")
        if not interests:
            errors.append("Interests are missing")

        if len(errors) != 0:
            return render_template('signup.html', errors=errors)

        db.execute('INSERT into hangout_info(id,fullname,number,interests) '
                   'VALUES (?,?,?,?)'
                   , (id, name, number, interests))

        flash('You have successfully registered')
        return render_template('signin.html')
    else:
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template('signup2.html')


@app.route('/checkuser', methods=['GET'])
def check():
    """Return true if username available, else false, in JSON format"""
    name = request.args.get('username')
    res = db.execute('SELECT EXISTS(SELECT 1 FROM users WHERE username=?)', (name,)).fetchone()

    if res[0] == 0:
        return 'true'
    else:
        return 'false'


@app.route('/logout', methods=['GET'])
def logout():
    """Return true if username available, else false, in JSON format"""
    session.clear()
    return redirect('/')


@app.route('/findpeople')
@login_required
def findpeople():
    users = db.execute(
        "SELECT users.username,email,fullname,number,interests,photoType,hangout_info.rating from users"
        " INNER JOIN hangout_info ON hangout_info.id=users.id").fetchall()

    return render_template('find_people.html', users=users)


def updateUserRating(user, rating):
    user = db.execute("SELECT id from users WHERE username=?", (user,)).fetchone()
    if user:
        userID = user[0]
    else:
        raise Exception('User not found')

    userRating = int(db.execute("Select rating From hangout_info WHERE id=?", (userID,)).fetchone()[0])
    userRating = int((int(userRating) + int(rating)) / 2)
    db.execute("UPDATE hangout_info SET rating=? WHERE id=?", (userRating, userID))


@app.route('/review', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        loggedUser = session['user_name']
        reviewedUser = request.form.get('username')
        places = request.form.get('place')
        rating = request.form.get('rating')
        description = request.form.get('desc')
        try:
            updateUserRating(reviewedUser, rating)
        except:
            return render_template('feedback.html', errormsg="User not found!!")

        db.execute("INSERT INTO reviews(logged_user,reviewed_user,places,rating,desc) values(?,?,?,?,?)", (loggedUser,
                                                                                                           reviewedUser,
                                                                                                           places,
                                                                                                           rating,
                                                                                                           description))
        flash("User reviewed successfully")
        return redirect('/')
    else:
        return render_template('feedback.html')


@app.route('/history')
@login_required
def history():
    user = session['user_name']
    data = db.execute("SELECT * from reviews WHERE logged_user=?", (user,)).fetchall()
    return render_template('history.html', data=data)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    username = session['user_name']
    info = db.execute(
        "SELECT fullname,email,photoType,password,interests,number from users"
        " INNER JOIN hangout_info ON hangout_info.id=users.id WHERE username=?", (username,)).fetchone()
    fullname = info[0]
    email = info[1]
    photoType = info[2]
    password = info[3]
    interests = info[4]
    number = info[5]

    if request.method == 'GET':
        print(info)
        return render_template('profile.html', info=info)
    else:
        if request.form.get('fullname') != '':
            fullname = request.form.get('fullname')
        if request.form.get('email') != '':
            email = request.form.get('email')
        if request.form.get('password') != '':
            password = generate_password_hash(request.form.get('password'))
        if request.form.get('number') != '':
            number = request.form.get('number')
        if request.form.get('interests') != '':
            interests = request.form.get('interests')
        if request.files.get('profile_photo'):
            photo = request.files.get('profile_photo')
            photoType = username + '.jpg'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photoType))

        db.execute("UPDATE hangout_info SET fullname=?,interests=?,number=? WHERE id=?"
                   , (fullname, interests, number, session['user_id']))
        db.execute("UPDATE users SET email=?,password=?,photoType=? WHERE username=?"
                   , (email, generate_password_hash(password), photoType, username))

        print(fullname, email, password)
        flash("Profile updated successfully!!")
        return redirect('/')
