from flask.cli import FlaskGroup
from src import app
import getpass
from src.accounts.models import User
from src.core.views import *
from src import bcrypt, db
from celery import Celery
import time
import os


cli = FlaskGroup(app)

# Celery configuration
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
# Initialize Celery
celery = Celery('src', broker='redis://localhost:6379/0')
celery.conf.update(app.config)

@celery.task(bind=True)
def user_password_long_task(self):
    """Background task that runs a long function with progress reports."""
    print("entrer-------------------user_password_____________long_task")
    for i in range(1,15):
        print(i)
    # password_modifying()
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 'Done'}

@celery.task
def run_sleeping_func(num):
    asyncio.run(sleeping_func(num))

@celery.task
def dowload_you_vid(video_id, vid_url):
    asyncio.run(you_download(video_id, vid_url))

#====================== IN TERMINAL:Run===>>python3 manage.py create_admin====================
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


if __name__ == "__main__":
    cli()



# source .env
# RUN PROJECT python3 manage.py run
#  RUN CELERY celery -A manage.celery worker --loglevel=info

## flask db init
## flask db migrate
## flask db upgrade

#====================== IN TERMINAL:Run===>>python3 manage.py create_admin====================
