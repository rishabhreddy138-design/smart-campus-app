from datetime import datetime
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    theme = db.Column(db.String(10), default='dark')
    
    materials = db.relationship('Material', backref='uploader', lazy=True)
    assignments = db.relationship('Assignment', backref='creator', lazy=True)
    submissions = db.relationship('Submission', backref='student', lazy=True)
    announcements = db.relationship('Announcement', backref='poster', lazy=True)
    badges = db.relationship('Badge', backref='user', lazy=True)
    profile = db.relationship('Profile', backref='user', lazy=True, uselist=False)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(300), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    attachment_path = db.Column(db.String(300), nullable=True)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic')

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(300), nullable=True)
    text_content = db.Column(db.Text, nullable=True)
    submitted_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='on-time')
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    badge_name = db.Column(db.String(100), nullable=False)
    earned_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.Text, nullable=True)
    department = db.Column(db.String(120), nullable=True)
    avatar_path = db.Column(db.String(300), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)