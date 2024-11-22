from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    roles = db.relationship('UserRole', backref='user', lazy=True)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.Password = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.Password, password)

class ProductOwner(db.Model):
    __tablename__ = 'productowners'

    ProductOwnerID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    ContactNumber = db.Column(db.String(15), nullable=False)

    # Relationship to ProjectInfo
    projects = db.relationship('ProjectInfo', backref='product_owner', lazy=True)

class ScrumMaster(db.Model):
    __tablename__ = 'scrummasters'

    ScrumMasterID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    ContactNumber = db.Column(db.String(15), nullable=False)

    # Relationship to Sprints
    sprints = db.relationship('Sprint', backref='scrum_master', lazy=True)

# ProjectInfo Table
class ProjectInfo(db.Model):
    __tablename__ = 'projectinfo'

    ProjectID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProjectName = db.Column(db.String(100), nullable=False)
    ProductOwnerID = db.Column(db.Integer, db.ForeignKey('productowners.ProductOwnerID'), nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=True)
    RevisedEndDate = db.Column(db.Date, nullable=True)
    Status = db.Column(db.String(50), nullable=False)

    # Relationships
    sprints = db.relationship('Sprint', backref='project', lazy=True)
    user_stories = db.relationship('UserStory', backref='project', lazy=True)


# Sprints Table
class Sprint(db.Model):
    __tablename__ = 'sprints'

    SprintID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProjectID = db.Column(db.Integer, db.ForeignKey('projectinfo.ProjectID'), nullable=False)
    ScrumMasterID = db.Column(db.Integer, db.ForeignKey('scrummasters.ScrumMasterID'), nullable=False)
    SprintNo = db.Column(db.Integer, nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=True)
    SprintStatus = db.Column(db.String(50), nullable=False)

    # Relationship to UserStories
    user_stories = db.relationship('UserStory', backref='sprint', lazy=True)


# UserRoles Table
class UserRole(db.Model):
    __tablename__ = 'userroles'

    RoleID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    ProjectID = db.Column(db.Integer, db.ForeignKey('projectinfo.ProjectID'), nullable=False)
    RoleName = db.Column(db.String(50), nullable=False)



# UserStories Table
class UserStory(db.Model):
    __tablename__ = 'userstories'

    UserStoriesID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProjectID = db.Column(db.Integer, db.ForeignKey('projectinfo.ProjectID'), nullable=False)
    SprintID = db.Column(db.Integer, db.ForeignKey('sprints.SprintID'), nullable=False)
    UserStory = db.Column(db.Text, nullable=False)
    Moscow = db.Column(db.String(10), nullable=False)  # MoSCoW prioritization
    Assignee = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    Status = db.Column(db.String(50), nullable=False)
    StoryPoints = db.Column(db.Integer, nullable=False)

    # Relationship to Tasks
    tasks = db.relationship('Task', backref='user_story', lazy=True)


# Tasks Table
class Task(db.Model):
    __tablename__ = 'tasks'

    TaskID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserStoriesID = db.Column(db.Integer, db.ForeignKey('userstories.UserStoriesID'), nullable=False)
    TaskName = db.Column(db.String(200), nullable=False)
    AssigneeUserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    TaskStatus = db.Column(db.String(50), nullable=False)
