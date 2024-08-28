from flask import Blueprint, render_template, flash, redirect, request, url_for, session
from flask_login import login_user, current_user, logout_user, login_required
from src.accounts.models import *
from src import bcrypt, db
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from threading import Thread
from manage import *
from flask_bcrypt import check_password_hash
import random
import os
from manage import *
import string


core_bp = Blueprint("core", __name__)


@core_bp.route("/")
@login_required
def home():
    print("home function------ >>>>>>>>>>>>>>>>>")
    user_list = User.query.filter_by(is_admin=False)
    site_user_list = SiteUser.query.all()
    print("site_user", site_user_list)

    for i in site_user_list:
        print("------", i)

    # for i in user_list:
    #     db.session.delete(i)
    #     db.session.commit()
    #     print(i,"deleted")
    # task = user_password_long_task.apply_async()
    return render_template("accounts/home.html", user_list=user_list, site_user_list=site_user_list)


@core_bp.route("/newlogin", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        # Get form data
        username_or_email = request.form.get("username_or_email")
        password = request.form.get("password")

        user = User.query.filter(User.email == username_or_email).first()

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['user_email'] = user.email
            flash("Login successful!", "success")
            return redirect(url_for('core.dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("accounts/login_form.html")


@core_bp.route("/new_register", methods=["GET", "POST"])
def register_page():
    user = get_session_user()
    print("user_register data", user)
    if request.method == "POST":
        # Extract form data
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")

        print("fullname", fullname)
        print("email", email)
        print("phone", phone)

        phone_last_three = phone[-3:]
        generated_username = f"{fullname}{phone_last_three}"

        # Generate a random 6-digit password
        random_password = ''.join(random.choices(string.digits, k=6))

        username = generated_username
        password = random_password

        print("username", username)
        print("password", password)

        # Check if the email or username already exists
        existing_user = SiteUser.query.filter(
            (SiteUser.email == email) | (SiteUser.username == username)
        ).first()

        if existing_user:
            flash("Email or username already exists.", "danger")
            return redirect(url_for('core.register_page'))

        # Create a new user instance
        new_user = SiteUser(
            fullname=fullname,
            username=username,
            password=password,
            email=email,
            phone=phone
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful", "success")
        return redirect(url_for('core.dashboard'))
    if user:
        return render_template("accounts/register_form.html", user=user)
    else:
        flash("You need to log in first.", "warning")
        return redirect(url_for('core.login_page'))


@core_bp.route("/dashboard")
def dashboard():
    print("dashboard- >>>>>>>>>>>>>>>>>")
    print(session['user_email'], "++++++++++")

    user = get_session_user()

    site_users = SiteUser.query.all()
    total_deposit = 10

    for i in site_users:

        total_deposit = total_deposit + i.investment

    print("user_dashboard data", user)
    print("total_deposit", total_deposit)
    if user:
        return render_template("accounts/dashboard.html", user=user, site_users=site_users)
    else:
        flash("You need to log in first.", "warning")
        return redirect(url_for('core.login_page'))


@core_bp.route('/user_list', methods=['GET'])
@login_required
def user_list():

    user = get_session_user()
    user_count = 0
    site_users = SiteUser.query.all()
    for site_users in site_users:
        user_count += 1

    return render_template("accounts/user_list.html", user=user, user_count=user_count)


@core_bp.route('/user_details', methods=['GET'])
# @core_bp.route('/user_card/<int:user_id>', methods=['GET'])
@login_required
def user_details():

    user = get_session_user()
    return render_template("accounts/user_details.html", user=user)


@core_bp.route('/delete/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    flash("User Deleted.", "success")
    return redirect(url_for("accounts.login"))


@core_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        email = request.form['email']
        pass_word = request.form['password']
        if pass_word:
            password = bcrypt.generate_password_hash(pass_word)
            user.password = password
        user.email = email
        db.session.commit()
        return redirect(url_for('core.home'))
    return render_template("accounts/update.html", user_data=user)


@core_bp.route('/send_otp', methods=["GET", "POST"])
def send_otp():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            otp = random.randint(100000, 999999)
            flash("You Password Reset Done!", "success")
            return redirect(url_for('accounts.login'))
        else:
            flash("Please Enter Valid Email")
    return render_template("accounts/forget_password.html")


@core_bp.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    if request.method == 'POST':
        email = request.form['email']
        pass_word = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and pass_word:
            if pass_word:
                password = bcrypt.generate_password_hash(pass_word)
                user.password = password
            db.session.commit()
            flash("You Password Reset Done!", "success")
            return redirect(url_for('accounts.login'))
        else:
            flash("Please Enter Valid Email")
    return render_template("accounts/forget_password.html")


@login_required
def password_modifying():
    user_list = User.query.filter_by(is_admin=False)
    for user in user_list:
        hashed_password = user.password
        print('hashed_password11111111111111: ', hashed_password)
        is_hashed = True
        try:
            # Change 'test' to an example password
            bcrypt.check_password_hash(hashed_password, 'test')
        except ValueError:
            is_hashed = False
        if is_hashed == False:
            hashed_password = bcrypt.generate_password_hash(
                hashed_password).decode('utf-8')
            print(f"Username: {user.email}, Is Hashed: {is_hashed}")
        print('hashed_password2222222222222222: ', hashed_password)


def get_session_user():
    user_email = session.get('user_email')
    if user_email:
        user = User.query.filter_by(email=user_email).first()
        return user
    return None
