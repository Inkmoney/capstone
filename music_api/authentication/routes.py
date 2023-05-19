from flask import Blueprint,flash, redirect, render_template, session
from music_api.helpers import my_spotify_client

from music_api.forms import (LoginForm, RegisterForm)
from music_api.models import User, db

auth = Blueprint('auth', __name__, template_folder='auth_templates')

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""
    if "user_id" in session:
        return redirect(f"/users/home/{session['user_id']}")
    form = RegisterForm()
    name = form.username.data
    pwd = form.password.data
    existing_user_count = User.query.filter_by(username=name).count()
    if existing_user_count > 0:
        flash("User already exists")
        return redirect('/login')

    if form.validate_on_submit():
        user = User.register(name, pwd)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        # on successful login, redirect to profile page
        return redirect(f"/users/home/{user.id}")
    else:
        return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("login.html", form=form)
    # otherwise
    name = form.username.data
    pwd = form.password.data
    # authenticate will return a user or False
    user = User.authenticate(name, pwd)

    if not user:
        return render_template("login.html", form=form)
    # otherwise

    form.username.errors = ["Bad name/password"]
    my_spotify_client.perform_auth()
    session["spotify_access_token"] = my_spotify_client.access_token
    session["spotify_access_token_expires"] = my_spotify_client.access_token_expires
    session["spotify_access_token_did_expire"] = my_spotify_client.access_token_did_expire
    session["user_id"] = user.id  
    return redirect(f"/users/home/{user.id}")



@auth.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""
    session.pop("user_id")
    
    return redirect("/login")