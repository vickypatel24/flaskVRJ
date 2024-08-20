from datetime import datetime
from flask_login import UserMixin # Add this line
from src import bcrypt, db
from flask_login import LoginManager # Add this line

login_manager = LoginManager() # Add this line


#

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    otp = db.Column(db.Integer, nullable=True)
    # img = db.Column(db.LargeBinary)

    def __init__(self, email, password, is_admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()
        self.is_admin = is_admin

    def __repr__(self):
        return f"<email {self.email}>"
    