from website.models import User
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db # from __init__.py file
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first() # check in db whether we have a user with the email submitted#
        
        if user:
            if check_password_hash(user.password, password): # user.password accesses the password for the user we queried above, we could also access any other value fo that user 
                flash('Logged in successfully', category='success')
                login_user(user, remember=True) # this logs the user in and remembers them using session cookie
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect. Please check your credentials', category='error')
        else:
            flash('email does not exist', category='error')


    #print(data)
    return render_template('login.html', user=current_user) # store the current user in 'user'

@auth.route('/logout')
@login_required # this decorator makes it so that this is only available to logged in users
def logout():
    logout_user() # this logs the user out - how easy!
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName') # this is the value of the relvant field () in the form submitted in the form in /sign-up (name=firstName)
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first() # check in db whether we have a user with the email submitted#

        if user: # if a user exists after the check above - prevents us adding users who already have an account
            flash('Email already exists',category='error')

        elif len(email) < 4:
            flash('email must be longer than 4 chars', category='error')
        elif len(first_name) < 2:
            flash('must be longer than 4 chars', category='error')
        elif password1 != password2:
            flash('passwords don\'t match', category='error')
        elif len(password1) < 7:
            flash('password must be longer than 7 chars', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True) # this logs the user in and remembers them using session cookie
            flash('Account created', category='success')

            return redirect(url_for('views.home'))


    return render_template('sign_up.html', user=current_user) # store the current user in 'user'