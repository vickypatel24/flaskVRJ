from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, current_user, logout_user, login_required
from src import bcrypt, db
from src.accounts.models import User
import email_validator


# Importing required functions

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/logout")
@login_required
def logout():
    print("log out function")
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("core.login_page"))