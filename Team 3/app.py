from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)

DATABASE = 'projects.db'

# Function to get database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return db

# Close database connection when the app context ends
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def dashboard():
    db = get_db()
    # Fetch project statistics
    total_projects = db.execute('SELECT COUNT(*) FROM ProjectInfo').fetchone()[0]
    active_projects = db.execute("SELECT COUNT(*) FROM ProjectInfo WHERE Status = 'Active'").fetchone()[0]
    on_hold_projects = db.execute("SELECT COUNT(*) FROM ProjectInfo WHERE Status = 'On Hold'").fetchone()[0]
    
    stats = {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "on_hold_projects": on_hold_projects,
    }

    # Fetch all projects with ProductOwner name using JOIN
    projects = db.execute('''
        SELECT p.ProjectID, p.ProjectName, p.StartDate, p.EndDate, p.RevisedEndDate, p.Status, po.Name
        FROM ProjectInfo p
        JOIN ProductOwner po ON p.ProductOwnerID = po.ProductOwnerID
    ''').fetchall()

    return render_template('dashboard.html', projects=projects, stats=stats)

@app.route('/project/<int:project_id>')
def project_overview(project_id):
    db = get_db()
    
    # Fetch project details, including ProductOwnerID
    project = db.execute(''' 
        SELECT p.ProjectID, p.ProjectName, p.ProductOwnerID, po.Name AS ProductOwnerName
        FROM ProjectInfo p
        JOIN ProductOwner po ON p.ProductOwnerID = po.ProductOwnerID
        WHERE p.ProjectID = ?;
    ''', (project_id,)).fetchone()

    if project:
        # Fetch sprints for the project
        sprints = db.execute('SELECT s.*, SUM(us.StoryPoints) AS TotalStoryPoints FROM Sprints s JOIN UserStories us ON s.SprintID = us.SprintID WHERE s.ProjectID = ? GROUP BY s.SprintID;', (project_id,)).fetchall()
        
        # Fetch user stories with UserName from Users table
        user_stories = db.execute(''' 
            SELECT us.UserStory, us.Status, us.Assignee, us.SprintId, u.UserName, us.Moscow, us.StoryPoints
            FROM UserStories us
            LEFT JOIN Users u ON us.Assignee = u.UserID
            WHERE us.ProjectID = ?
        ''', (project_id,)).fetchall()
        product_owner = db.execute(''' 
            SELECT * FROM ProductOwner WHERE ProductOwnerID = ?;
        ''', (project[2],)).fetchone()
        users = db.execute('SELECT UserID, UserName FROM Users').fetchall()
        # Pass the ProductOwnerName along with other data
        return render_template('project_overview.html', product_owner=product_owner, project=project, sprints=sprints, user_stories=user_stories, users=users)
    else:
        return "Project not found", 404

@app.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    db = get_db()
    
    # Fetch project details along with the product owner name
    project = db.execute('''
        SELECT p.ProjectID, p.ProjectName, p.ProductOwnerID, p.StartDate, p.EndDate, p.RevisedEndDate, p.Status, po.Name
        FROM ProjectInfo p
        JOIN ProductOwner po ON p.ProductOwnerID = po.ProductOwnerID
        WHERE p.ProjectID = ?;
    ''', (project_id,)).fetchone()

    if project:
        if request.method == 'POST':
            # Retrieve form data
            name = request.form['name']
            product_owner_id = request.form['product_owner_id']  # Updated field name
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            revised_date = request.form['revised_date']
            status = request.form['status']
            
            # Update project in the database
            db.execute('''
                UPDATE ProjectInfo
                SET ProjectName = ?, ProductOwnerID = ?, StartDate = ?, EndDate = ?, RevisedEndDate = ?, Status = ?
                WHERE ProjectID = ?
            ''', (name, product_owner_id, start_date, end_date, revised_date, status, project_id))
            
            db.commit()
            
            return redirect(url_for('project_overview', project_id=project_id))
        
        # Fetch the list of available product owners for the select dropdown (assuming you have multiple owners)
        product_owners = db.execute('SELECT ProductOwnerID, Name FROM ProductOwner').fetchall()
        
        return render_template('edit_project.html', project=project, product_owners=product_owners)
    else:
        return "Project not found", 404

@app.route('/project/update/<int:project_id>', methods=['POST'])
def update_project(project_id):
    db = get_db()
    
    # Get the form data
    name = request.form['name']
    product_owner_id = request.form['product_owner_id']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    revised_date = request.form['revised_date']
    status = request.form['status']
    
    # Update project in the database
    db.execute('''
        UPDATE ProjectInfo
        SET ProjectName = ?, ProductOwnerID = ?, StartDate = ?, EndDate = ?, RevisedEndDate = ?, Status = ?
        WHERE ProjectID = ?
    ''', (name, product_owner_id, start_date, end_date, revised_date, status, project_id))
    
    db.commit()
    
    # Redirect to the project overview page after updating
    return redirect(url_for('project_overview', project_id=project_id))


@app.route('/project/update_user_story/<int:project_id>', methods=['POST'])
def update_user_story(project_id):
    db = get_db()
    
    # Loop through the user stories and update based on the form data
    for story in request.form:
        if story.startswith('status_'):
            user_story_id = story.split('_')[1]
            status = request.form[story]
            sprint_id = request.form.get(f'sprint_{user_story_id}')
            
            # Update the status and sprint for the user story
            db.execute('''
                UPDATE UserStories
                SET Status = ?, SprintId = ?
                WHERE UserStoryID = ? AND ProjectID = ?
            ''', (status, sprint_id, user_story_id, project_id))
    
    db.commit()
    return redirect(url_for('project_overview', project_id=project_id))


if __name__ == '__main__':
    app.run(debug=True)  