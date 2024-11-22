from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Sprint, ProjectInfo, ScrumMaster, ProductOwner, UserRole, UserStory, Task
from werkzeug.security import generate_password_hash
from datetime import datetime
from config import Config  # Ensure you have a config.py file for configuration
from flask import Flask, jsonify

# Initialize the Flask app
app = Flask(__name__)
app.config.from_object(Config)  # Import your config settings

# Set a secret key (important for session management)
app.secret_key = b'\xb1\x9f\xbe\xa1\xc8s\xd3\xe2\xc6\xd7v5\x16\xe2g\xe0\x8e\x9b\xeb\xadF\xf3\xb9\xbf'  # Use a random, unique key here

# Initialize the database with the app
db.init_app(app)

# Routes definition

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Add User route
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if username or email already exists
        existing_user = User.query.filter((User.UserName == username) | (User.Email == email)).first()
        if existing_user:
            flash('Username or Email already exists!', 'danger')
            return redirect(url_for('add_user'))

        # Hash the password before saving it
        hashed_password = generate_password_hash(password)

        # Create a new User instance
        new_user = User(UserName=username, Email=email, Password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect after successful form submission
        flash('User added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_user.html')

# Add ProductOwner route
@app.route('/add_productOwner', methods=['GET', 'POST'])
def add_productOwner():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']

        # Create a new ProductOwner instance
        new_product_owner = ProductOwner(Name=name, Email=email, ContactNumber=contact)

        # Add the new product owner to the database
        db.session.add(new_product_owner)
        db.session.commit()

        # Redirect to the home page
        flash('Product Owner added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_productOwner.html')

# Add ScrumMaster route
@app.route('/add_scrumMaster', methods=['GET', 'POST'])
def add_scrumMaster():
    if request.method == 'POST':
        email = request.form['email']
        contact = request.form['contact']

        # Create a new ScrumMaster instance
        new_scrum_master = ScrumMaster(Email=email, ContactNumber=contact)

        # Add the new scrum master to the database
        db.session.add(new_scrum_master)
        db.session.commit()

        # Redirect to the home page
        flash('Scrum Master added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_scrumMaster.html')

# Route for adding a new project
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        product_owner_id = request.form['product_owner_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        revised_end_date = request.form['revised_end_date']
        status = request.form['status']

        # Validate date formats and other fields as needed
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            revised_end_date = datetime.strptime(revised_end_date, '%Y-%m-%d').date() if revised_end_date else None
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('add_project'))

        # Create a new ProjectInfo instance
        new_project = ProjectInfo(
            ProjectName=project_name,
            ProductOwnerID=product_owner_id,
            StartDate=start_date,
            EndDate=end_date,
            RevisedEndDate=revised_end_date,
            Status=status
        )

        # Add the new project to the database
        db.session.add(new_project)
        db.session.commit()

        # Flash success message and redirect
        flash('Project added successfully!', 'success')
        return redirect(url_for('home'))

    # Fetch available Product Owners for the dropdown
    product_owners = ProductOwner.query.all()

    return render_template('add_project.html', product_owners=product_owners)

# Route for adding a new sprint
@app.route('/add_sprint', methods=['GET', 'POST'])
def add_sprint():
    if request.method == 'POST':
        # Get the form data
        project_id = request.form['project_id']
        scrum_master_id = request.form['scrum_master_id']
        sprint_no = request.form['sprint_no']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        sprint_status = request.form['sprint_status']
        
        # Convert the date strings to datetime.date objects
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('add_sprint'))

        # Create a new Sprint object
        new_sprint = Sprint(
            ProjectID=project_id,
            ScrumMasterID=scrum_master_id,
            SprintNo=sprint_no,
            StartDate=start_date,
            EndDate=end_date,
            SprintStatus=sprint_status
        )

        # Add to the session and commit to the database
        try:
            db.session.add(new_sprint)
            db.session.commit()
            flash('Sprint added successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to home or another page
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f'Error: {str(e)}', 'danger')

    # If GET request, display the add sprint form
    projects = ProjectInfo.query.all()  # Get all projects
    scrum_masters = ScrumMaster.query.all()  # Get all scrum masters
    return render_template('add_sprint.html', projects=projects, scrum_masters=scrum_masters)



@app.route('/add_user_role', methods=['GET', 'POST'])
def add_user_role():
    if request.method == 'POST':
        # Get the form data
        user_id = request.form['user_id']
        project_id = request.form['project_id']
        role_name = request.form['role_name']

        # Create a new UserRole object
        new_role = UserRole(
            UserID=user_id,
            ProjectID=project_id,
            RoleName=role_name
        )

        # Add to the session and commit to the database
        try:
            db.session.add(new_role)
            db.session.commit()
            flash('Role added successfully!', 'success')
            return redirect(url_for('add_user_role'))  # Redirect to the same page or another page
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f'Error: {str(e)}', 'danger')

    # If GET request, display the add user role form
    users = User.query.all()  # Get all users
    projects = ProjectInfo.query.all()  # Get all projects
    return render_template('add_user_role.html', users=users, projects=projects)



from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, UserStory, ProjectInfo, Sprint, User

@app.route('/add_user_story', methods=['GET', 'POST'])
def add_user_story():
    if request.method == 'POST':
        # Get form data
        project_id = request.form.get('project_id')
        sprint_id = request.form.get('sprint_id')
        user_story = request.form.get('user_story')
        moscow = request.form.get('moscow')
        assignee = request.form.get('assignee')
        status = request.form.get('status')
        story_points = request.form.get('story_points')

        # Validate inputs (optional but recommended)
        if not all([project_id, sprint_id, user_story, moscow, assignee, status, story_points]):
            flash("All fields are required.", "danger")
            return redirect(url_for('add_user_story'))

        # Add the new UserStory to the database
        try:
            new_story = UserStory(
                ProjectID=int(project_id),
                SprintID=int(sprint_id),
                UserStory=user_story,
                Moscow=moscow,
                Assignee=int(assignee),
                Status=status,
                StoryPoints=int(story_points)
            )
            db.session.add(new_story)
            db.session.commit()
            flash("User story added successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")

    # On GET request, render the form
    projects = ProjectInfo.query.all()
    sprints = Sprint.query.all()
    users = User.query.all()
    return render_template('add_user_story.html', projects=projects, sprints=sprints, users=users)



@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        # Retrieve form data
        user_story_id = request.form['user_story_id']
        task_name = request.form['task_name']
        assignee_user_id = request.form['assignee_user_id']
        task_status = request.form['task_status']

        # Create a new Task object
        new_task = Task(
            UserStoriesID=user_story_id,
            TaskName=task_name,
            AssigneeUserID=assignee_user_id,
            TaskStatus=task_status
        )

        # Add the task to the database
        try:
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to the home or task list page
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding task: {str(e)}', 'danger')

    # Fetch data for the dropdowns
    user_stories = UserStory.query.all()
    users = User.query.all()

    return render_template('add_task.html', user_stories=user_stories, users=users)
# Donut Chart
@app.route('/chart-data/donut')
def donut_chart_data():
    # Query to count tasks by status
    data = db.session.query(Task.TaskStatus, db.func.count(Task.TaskID)).group_by(Task.TaskStatus).all()
    labels = [item[0] for item in data]
    values = [item[1] for item in data]

    return {"labels": labels, "values": values}


# Burnup chart 
import matplotlib.pyplot as plt
import io
import base64
from flask import Response
@app.route('/chart-data/burnup')
def burnup_chart_data():
    # Fetching user stories data (for a specific project)
    project_id = 1  # Replace with dynamic project ID if needed
    user_stories = UserStory.query.filter_by(ProjectID=project_id).all()

    # Group data by SprintID
    completed_sprint = {}
    not_completed_sprint = {}

    # Calculate story points for completed and not completed tasks
    for us in user_stories:
        if us.Status == 'Completed':
            completed_sprint[us.SprintID] = completed_sprint.get(us.SprintID, 0) + us.StoryPoints
        elif us.Status in ['In Progress', 'Not Started']:
            not_completed_sprint[us.SprintID] = not_completed_sprint.get(us.SprintID, 0) + us.StoryPoints

    sprint_ids = sorted(set([us.SprintID for us in user_stories]))
    completed_data = [completed_sprint.get(sprint_id, 0) for sprint_id in sprint_ids]
    not_completed_data = [not_completed_sprint.get(sprint_id, 0) for sprint_id in sprint_ids]
    total_effort = [completed + not_completed for completed, not_completed in zip(completed_data, not_completed_data)]

    # Map SprintIDs to Sprint Numbers (e.g., Sprint 1, Sprint 2, etc.)
    sprint_numbers = [f'Sprint {i+1}' for i in range(len(sprint_ids))]

    return {
        "sprint_ids": sprint_numbers,  # Return sprint numbers instead of SprintID
        "completed_data": completed_data,
        "not_completed_data": not_completed_data,
        "total_effort": total_effort
    }


# Velocity chart 
@app.route('/chart-data/velocity')
def velocity_chart_data():
    # Fetching user stories data (for a specific project)
    project_id = 1  # Replace with dynamic project ID if needed
    user_stories = UserStory.query.filter_by(ProjectID=project_id).all()

    # Group data by SprintID
    total_story_points = {}
    completed_story_points = {}

    # Calculate total story points and completed story points for each sprint
    for us in user_stories:
        total_story_points[us.SprintID] = total_story_points.get(us.SprintID, 0) + us.StoryPoints
        if us.Status == 'Completed':
            completed_story_points[us.SprintID] = completed_story_points.get(us.SprintID, 0) + us.StoryPoints

    sprint_ids = sorted(set([us.SprintID for us in user_stories]))
    total_data = [total_story_points.get(sprint_id, 0) for sprint_id in sprint_ids]
    completed_data = [completed_story_points.get(sprint_id, 0) for sprint_id in sprint_ids]

    # Map SprintIDs to Sprint Numbers (e.g., Sprint 1, Sprint 2, etc.)
    sprint_numbers = [f'Sprint {i+1}' for i in range(len(sprint_ids))]

    return {
        "sprint_ids": sprint_numbers,  # Return sprint numbers instead of SprintID
        "total_data": total_data,  # Total story points per sprint
        "completed_data": completed_data  # Completed story points per sprint
    }

@app.route('/chart-data/burndown')
def burndown_chart_data():
    # Fetching user stories data (for a specific project)
    project_id = 1  # Replace with dynamic project ID if needed
    user_stories = UserStory.query.filter_by(ProjectID=project_id).all()

    # Group data by SprintID
    remaining_sprint = {}

    # Calculate remaining story points for incomplete tasks
    for us in user_stories:
        if us.Status != 'Completed':
            remaining_sprint[us.SprintID] = remaining_sprint.get(us.SprintID, 0) + us.StoryPoints

    sprint_ids = sorted(set([us.SprintID for us in user_stories]))
    remaining_data = [remaining_sprint.get(sprint_id, 0) for sprint_id in sprint_ids]

    # Calculate the ideal burn (linear reduction of remaining work)
    ideal_burn = [remaining_data[0] - (remaining_data[0] / len(sprint_ids)) * i for i in range(len(sprint_ids))]

    # Map SprintIDs to Sprint Numbers (e.g., Sprint 1, Sprint 2, etc.)
    sprint_numbers = [f'Sprint {i+1}' for i in range(len(sprint_ids))]

    return {
        "sprint_ids": sprint_numbers,  # Return sprint numbers instead of SprintID
        "remaining_data": remaining_data,
        "ideal_burn": ideal_burn
    }


@app.route('/charts')
def charts():
    return render_template('charts.html')


# Main run condition
if __name__ == '__main__':
    app.run(debug=True)
