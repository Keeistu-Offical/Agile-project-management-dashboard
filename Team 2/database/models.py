# database/models.py
from database.db import db
from datetime import datetime

class Sprint(db.Model):
    __tablename__ = 'sprints'
    #sprint_id = db.Column(db.Integer, primary_key=True)
    sprint_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), nullable=False)

class UserStory(db.Model):
    __tablename__ = 'user_stories'
    story_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    efforts = db.Column(db.Integer, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), nullable=False)

class Project(db.Model):
    __tablename__ = 'projects'

    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    project_owner = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    revised_end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False)

    sprints = db.relationship('Sprint', backref='project', lazy=True)
    user_stories = db.relationship('UserStory', backref='project', lazy=True)