# database/queries.py
from database.models import Project
from database.db import db

def add_project(project_data):
    """Add a new project to the database."""
    new_project = Project(**project_data)
    db.session.add(new_project)
    db.session.commit()

def get_all_projects():
    """Retrieve all projects from the database."""
    return Project.query.all()
