#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
from tempfile import mkdtemp

from flask import Flask, flash, render_template
from flask_session import Session
from werkzeug.security import check_password_hash, \
    generate_password_hash

# Configure application
from helpers import *

app = Flask(__name__)

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
        # if requests.get(request.url+'/checkuser', 'username=' + username) == 'false':
        #     errors.append("Username is already taken!")
        if len(errors) != 0:
            return render_template('signup.html', errors=errors)

        db.execute('INSERT into users(username,email,password) '
                   'VALUES (?,?,?)'
                   , (username, email, generate_password_hash(password)))
        id = db.execute('SELECT id from users where username=?', (username,)).fetchone()[0]
        session['user_id'] = id;
        flash('You have successfully registered')
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
def finpeople():
    """Show portfolio of stocks"""
    return render_template('find_people.html')
