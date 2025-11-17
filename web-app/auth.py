"""Authorization module for the web app"""

import models
from db import db
from flask import Blueprint, flash, request
from flask_login import current_user, login_required, login_user, logout_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login route"""

    if current_user.is_authenticated:
        return "User is already authenticated"

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash("Please provide both a username and password", "error")

        user = models.User(db.users.find_one({"username": username}))
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return f"User logged in {user.username}"

        flash("Login Unsuccessful. Please check username and password", "danger")
    return "Login Page"


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    if current_user.is_authenticated:
        return "User is already authenticated"
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        existing_user = db.users.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please choose a different one.", "warning")
        else:
            user = models.User({"username": username})
            user.set_password(password)
            inserted_id = db.users.insert_one(user.to_dict())
            login_user(models.User(db.users.find_one({"_id": inserted_id.inserted_id})))
            flash("Logged in successfully!", "success")
            print("HELLOOO")
            return f"User logged in {user.username}"
    return "Registration page"


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout current logged in user"""
    logout_user()
    flash("You have been logged out.", "info")
    return "User has been logged out"
