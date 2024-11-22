from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message


# Initialize Flask app and set up SQLite database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agile_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or any other SMTP server
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'your_email_address'  # Your email address
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Your email password
mail = Mail(app)



# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User model to interact with the users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Route to display the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database for the user
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        
        msg= Message("Forgot password?", sender='noreply@demo.com', recipients= ['ankitaisadoctor@gmail.com'])
        msg.body = "We received a request to reset your password"
        mail.send(msg)
        flash('A password reset link has been sent to your email.', 'info')
    return render_template('forgotpassword.html')


@app.route('/reset_password')
def reset_password():
    if request.method == 'POST':
            new_password = request.form['new-password']
            # Here, you should hash the new password and update the user's password in the database
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('reset_password'))
    return render_template('reset_password.html')




# Route for the dashboard after successful login
@app.route('/dashboard')
def dashboard():
    return "Welcome to the Dashboard!"

# Main block to run the app
if __name__ == '__main__':
    app.run(debug=True)