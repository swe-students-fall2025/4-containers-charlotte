"""Authorization module for the web app"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

import models
from db import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login route"""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Please provide both a username and password", "error")
            return render_template("login.html")

        user_data = db.users.find_one({"username": username})

        if not user_data:
            flash("Login unsuccessful. Please check username and password.", "danger")
            return render_template("login.html")

        user = models.User(user_data)

        if user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))

        flash("Login unsuccessful. Please check username and password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirmed_p = request.form["confirmPassword"]

        existing_user = db.users.find_one({"username": username})

        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return render_template("register.html")

        if password != confirmed_p:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        user = models.User({"username": username})
        user.set_password(password)

        inserted = db.users.insert_one(user.to_dict())
        new_user = db.users.find_one({"_id": inserted.inserted_id})

        login_user(models.User(new_user))
        flash("Registered and logged in successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout current logged in user"""

    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
