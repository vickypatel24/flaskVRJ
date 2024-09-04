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
from flask_mail import Mail, Message

mail = Mail(app)

core_bp = Blueprint("core", __name__)


@core_bp.route("/dashboard")
@login_required
def dashboard():
    print("dashboard- >>>>>>>>>>>>>>>>>")
    print(session['user_email'], "++++++++++")

    user = get_session_user()

    site_users = SiteUser.query.all()
    total_deposit = 0

    for i in site_users:

        total_deposit = total_deposit + i.investment

    print("user_dashboard data", user)
    print("total_deposit", total_deposit)
    if user:
        context = {
            'user': user,
            'site_users': site_users,
            'total_deposit': total_deposit
        }
        return render_template("accounts/dashboard.html", **context)
    else:
        flash("You need to log in first.", "warning")
        return redirect(url_for('core.login_page'))


@core_bp.route("/new_register", methods=["GET", "POST"])
def register_page():
    user = get_session_user()
    print("user_register data", user)
    if request.method == "POST":
        # Extract form data
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        investment = request.form.get("investment")

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
            phone=phone,
            investment=investment
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


@core_bp.route('/user_list', methods=['GET'])
@login_required
def user_list():
    user = get_session_user()
    user_count = 0
    site_users = SiteUser.query.all()
    for site_user in site_users:
        user_count += 1
        print("-----------site_user", site_user.created_on)

    return render_template("accounts/user_list.html", user=user, user_count=user_count, site_users=site_users)


@core_bp.route('/user_details/<int:user_id>', methods=['GET'])
# @core_bp.route('/user_card/<int:user_id>', methods=['GET'])
@login_required
def user_details(user_id):
    print("details________page", user_id)
    site_user = SiteUser.query.get(user_id)
    user = get_session_user()
    return render_template("accounts/user_details.html", user=user, site_user=site_user)


@core_bp.route('/delete_user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    print("++++++++delete_user API")
    user = SiteUser.query.filter_by(id=user_id).first()
    print("User Deleted.-------------", user.fullname)
    # db.session.delete(user)
    # db.session.commit()
    flash("User Deleted.", "success")
    return redirect(url_for("core.user_list"))


@core_bp.route('/reste_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def reste_password(user_id):
    user = get_session_user()
    print("reste_passwoooooord", user)
    print("request.method", request.method)
    if request.method == 'POST':
        print("request.method POSTTTTT", )
        site_user = SiteUser.query.filter_by(id=user_id).first()
        password = request.form.get("password")
        print("password", password)
        if password:
            site_user.password = password
        db.session.commit()
        return redirect(url_for('core.dashboard'))
    return render_template("accounts/reset_password.html", user=user, site_user_id=user_id)



@core_bp.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    if request.method == 'POST':
        # from src import mail
        email = request.form['email']
        print("email>>>>>>>>>>>>>>>>>>>>", email)
        user = User.query.filter_by(email=email).first()

        if user:
            new_pass = random.randint(100000, 999999)
            print("new_pass-------------------", new_pass)

            sendmail = sending_mail(email, new_pass)
            # try:
            #     print("try____________startttttttttttttttttttt")
            #     msg = Message(
            #         subject=f"Your new Password is {new_pass}",
            #         recipients=[user.email]
            #     )
            #     print("+++++++++++++++++", msg)
            #     msg.body = f"Your new password is {new_pass}. Please use this to log in."
            #     mail.send(msg)

            #     # # Update the user's password
            #     # user.password = generate_password_hash(str(new_pass))  # Make sure to hash the password
            #     # db.session.commit()

            #     # flash("A new password has been sent to your email.", "success")

            # except Exception as e:
            #     return f"Failed to send email: {str(e)}"
            return redirect(url_for('core.login_page'))
        else:
            flash("Please enter a valid email address.", "danger")

    return render_template("accounts/forget_password.html")


# @core_bp.route('/forget_password', methods=["GET", "POST"])
# def forget_password():
#     if request.method == 'POST':
#         email = request.form['email']
#         pass_word = request.form['password']
#         user = User.query.filter_by(email=email).first()
#         if user and pass_word:
#             if pass_word:
#                 password = bcrypt.generate_password_hash(pass_word)
#                 user.password = password
#             db.session.commit()
#             flash("You Password Reset Done!", "success")
#             return redirect(url_for('accounts.login'))
#         else:
#             flash("Please Enter Valid Email")
#     return render_template("accounts/forget_password.html")


# @core_bp.route('/send_otp', methods=["GET", "POST"])
# def send_otp():
#     if request.method == 'POST':
#         email = request.form['email']
#         user = User.query.filter_by(email=email).first()
#         if user:
#             otp = random.randint(100000, 999999)
#             flash("You Password Reset Done!", "success")
#             return redirect(url_for('accounts.login'))
#         else:
#             flash("Please Enter Valid Email")
#     return render_template("accounts/forget_password.html")


def get_session_user():
    user_email = session.get('user_email')
    if user_email:
        user = User.query.filter_by(email=user_email).first()
        return user
    return None
