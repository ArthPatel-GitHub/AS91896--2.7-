# models/models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# FINAL: Movie Model for Static Images
class Movie(db.Model):
    __bind_key__ = 'movies'
    # __tablename__ = 'teaser_iamges' # <--- REMOVED: No longer needed for default 'movie' table
    id = db.Column(db.Integer, primary_key=True)
    # titles = db.Column('titles', db.String(255), nullable=False) # <--- REMOVED: Reverted to 'title'
    # images = db.Column('images', db.String(500), nullable=False, unique=True) # <--- REMOVED: Reverted to 'image_filename'
    title = db.Column(db.String(255), nullable=False) # <--- RESTORED: Back to 'title'
    image_filename = db.Column(db.String(255), nullable=False, unique=True) # <--- RESTORED: Back to 'image_filename'

    def __repr__(self):
        return f'<Movie {self.title}>'