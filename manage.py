from flask.cli import FlaskGroup
from src import app
import getpass
from src.accounts.models import User
from src.core.views import *
from src import bcrypt, db
from celery import Celery
import time
import os
from dotenv import load_dotenv

load_dotenv()

cli = FlaskGroup(app)

app = Flask(__name__)

# Celery configuration
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

app.config['UPLOAD_FOLDER'] = 'uploads'

# Access environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", None)
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", None)
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", None)
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER", None)

# mail = Mail(app)


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
# Initialize Celery
celery = Celery('src', broker='redis://localhost:6379/0')
celery.conf.update(app.config)


@celery.task(bind=True)
def user_password_long_task(self):
    """Background task that runs a long function with progress reports."""
    print("entrer-------------------user_password_____________long_task")
    for i in range(1, 15):
        print(i)
    # password_modifying()
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 'Done'}


# ====================== IN TERMINAL:Run===>>python3 manage.py create_admin====================


@cli.command("create_admin")
def create_admin():
    """Creates the admin user."""
    email = input("Enter email address: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Enter password again: ")
    if password != confirm_password:
        print("Passwords don't match")
        return 1
    try:
        user = User(email=email, password=password, is_admin=True)
        db.session.add(user)
        db.session.commit()
    except Exception:
        print("Couldn't create admin user.")


def sending_mail(email,new_pass):
    try:
        print("try____________startttttttttttttttttttt")
        msg = Message(
            subject=f"Your new Password is {new_pass}",
            recipients=[email]
        )
        print("+++++++++++++++++", msg)
        msg.body = f"Your new password is {new_pass}. Please use this to log in."
        mail.send(msg)

        # # Update the user's password
        # user.password = generate_password_hash(str(new_pass))  # Make sure to hash the password
        # db.session.commit()

        # flash("A new password has been sent to your email.", "success")

    except Exception as e:
        return   f"Failed to send email: {str(e)}"

if __name__ == "__main__":
    cli()


# source .env
# RUN PROJECT python3 manage.py run
#  RUN CELERY celery -A manage.celery worker --loglevel=info

# flask db init
# flask db migrate
# flask db upgrade

# ====================== IN TERMINAL:Run===>>python3 manage.py create_admin====================
