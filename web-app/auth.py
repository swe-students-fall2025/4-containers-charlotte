"""Authorization module for the web app"""

from flask import flash, request
from flask_login import current_user, login_required, login_user, logout_user

import models
from app import app
from db import get_history_collection


def get_user_collection():
    """Helper to get the users collection from the unified DB client."""
    history_collection = get_history_collection()
    return history_collection.database.users


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login route"""

    if current_user.is_authenticated:
        return "User is already authenticated"

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Please provide both a username and password", "error")

        users = get_user_collection()
        user = users.find_one({"username": username})

        if user and user.check_password(password):
            login_user(models.User(user))
            flash("Logged in successfully!", "success")
            return f"User logged in: {username}"

        flash("Login Unsuccessful. Please check username and password", "danger")

    return "Login Page"


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    if current_user.is_authenticated:
        return "User is already authenticated"

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = get_user_collection()
        existing_user = users.find_one({"username": username})

        if existing_user:
            flash("Username already exists. Please choose a different one.", "warning")
        else:
            user = models.User({"username": username})
            user.set_password(password)

            inserted_id = users.insert_one(user.to_dict()).inserted_id
            new_user = users.find_one({"_id": inserted_id})

            login_user(models.User(new_user))
            flash("Registered and logged in successfully!", "success")
            return f"User registered: {username}"

    return "Registration Page"


@app.route("/logout")
@login_required
def logout():
    """Logout current logged in user"""
    logout_user()
    flash("You have been logged out.", "info")
    return "User has been logged out"
