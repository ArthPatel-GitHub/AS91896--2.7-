from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
import datetime
from datetime import datetime as dt # Import datetime module specifically for current time

# --- OPTIONAL: For loading environment variables from a .env file ---
from dotenv import load_dotenv
load_dotenv()

# --- Flask-Mail Imports and Configuration ---
from flask_mail import Mail, Message

# --- Flask-SQLAlchemy Imports and Configuration ---
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.urandom(24) 

# --- Flask-Mail Configuration ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')
mail = Mail(app)

# --- Flask-SQLAlchemy Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # Initialize the database object

# --- Database User Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Primary key, auto-increments
    username = db.Column(db.String(20), unique=True, nullable=False) # UNIQUE USERNAME
    email = db.Column(db.String(120), unique=True, nullable=False)    # UNIQUE EMAIL
    dob = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)     # OPTIONAL & NULLABLE PHONE
    password = db.Column(db.String(60), nullable=False)              # NON-UNIQUE PASSWORD (HASHED)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# --- Temporarily store password reset codes/tokens (still in-memory for demo!) ---
password_reset_codes = {}

@app.route('/')
def home():
    movies = [
        {'title': 'The Shawshank Redemption', 'image_filename': 'movie1.jpg'},
        {'title': 'The Godfather', 'image_filename': 'movie2.jpg'},
        {'title': 'The Dark Knight', 'image_filename': 'movie3.jpg'},
        {'title': 'Pulp Fiction', 'image_filename': 'movie4.jpg'},
        {'title': 'The Lord of the Rings: The Return of the King', 'image_filename': 'movie5.jpg'},
        {'title': 'Forrest Gump', 'image_filename': 'movie6.jpg'},
        {'title': 'Inception', 'image_filename': 'movie7.jpg'},
        {'title': 'The Matrix', 'image_filename': 'movie8.jpg'},
        {'title': 'Goodfellas', 'image_filename': 'movie9.jpg'},
        {'title': 'Spirited Away', 'image_filename': 'movie10.jpg'},
        {'title': 'Interstellar', 'image_filename': 'movie11.jpg'},
        {'title': 'Parasite', 'image_filename': 'movie12.jpg'},
        {'title': 'Gladiator', 'image_filename': 'movie13.jpg'},
        {'title': 'The Lion King', 'image_filename': 'movie14.jpg'},
        {'title': 'Toy Story', 'image_filename': 'movie15.jpg'},
        {'title': 'Django Unchained', 'image_filename': 'movie16.jpg'},
        {'title': 'Inglourious Basterds', 'image_filename': 'movie17.jpg'},
        {'title': 'The Prestige', 'image_filename': 'movie18.jpg'},
        {'title': 'Saving Private Ryan', 'image_filename': 'movie19.jpg'},
        {'title': 'Avatar', 'image_filename': 'movie20.jpg'},
        {'title': 'Titanic', 'image_filename': 'movie21.jpg'},
        {'title': 'Jurassic Park', 'image_filename': 'movie22.jpg'},
        {'title': 'E.T. the Extra-Terrestrial', 'image_filename': 'movie23.jpg'},
        {'title': 'Star Wars: A New Hope', 'image_filename': 'movie24.jpg'},
        {'title': 'Back to the Future', 'image_filename': 'movie25.jpg'},
        {'title': 'The Terminator', 'image_filename': 'movie26.jpg'},
        {'title': 'Alien', 'image_filename': 'movie27.jpg'},
        {'title': 'Blade Runner 2049', 'image_filename': 'movie28.jpg'},
        {'title': "Schindler's List", 'image_filename': 'movie29.jpg'},
        {'title': 'The Departed', 'image_filename': 'movie30.jpg'}
    ]
    return render_template('home.html', movies=movies)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier'] 
        password = request.form['password']

        user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()

        if user and check_password_hash(user.password, password): 
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main_page'))
        else:
            flash('Invalid email/phone or password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        dob = request.form['dob']
        phone = request.form.get('phone') 
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic validation
        if not username or not email or not dob or not password or not confirm_password:
            flash('All fields marked with * are required.', 'danger')
            return render_template('signup.html', form_data=request.form)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html', form_data=request.form)

        if len(password) < 6: 
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('signup.html', form_data=request.form)

        # --- Check if username or email already exists in DATABASE (Ensures uniqueness) ---
        existing_user_username = User.query.filter_by(username=username).first()
        existing_user_email = User.query.filter_by(email=email).first()
        
        if existing_user_username:
            flash('Username already taken.', 'danger')
            return render_template('signup.html', form_data=request.form)
        if existing_user_email:
            flash('Email already registered.', 'danger')
            return render_template('signup.html', form_data=request.form)
        
        # Check phone only if provided, and ensure it's unique if it exists
        if phone and User.query.filter_by(phone=phone).first():
            flash('Phone number already registered.', 'danger')
            return render_template('signup.html', form_data=request.form)


        hashed_password = generate_password_hash(password)
        
        # --- Handle optional phone number: convert empty string to None ---
        # This is the line that allows multiple users to omit a phone number
        # without violating the UNIQUE constraint on the 'phone' column.
        phone_to_save = phone if phone else None 
        
        new_user = User(username=username, email=email, dob=dob, phone=phone_to_save, password=hashed_password)
        db.session.add(new_user) 
        db.session.commit()      

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/main')
def main_page():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('placeholder_main.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# --- FORGOT PASSWORD ROUTES ---

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        
        user = User.query.filter_by(email=email).first() 

        if user:
            reset_code = secrets.token_urlsafe(6)
            expires_at = dt.now() + datetime.timedelta(minutes=15)

            password_reset_codes[email] = {'code': reset_code, 'expires_at': expires_at, 'used': False}

            try:
                msg = Message("My Movie Site - Password Reset Request",
                              sender=app.config['MAIL_DEFAULT_SENDER'],
                              recipients=[email])
                msg.body = f"""Hello,

You recently requested to reset your password for My Movie Site.

Your password reset code is:
{reset_code}

This code is valid for the next 15 minutes.

If you did not request a password reset, please ignore this email.

Thanks,
The My Movie Site Team
"""
                mail.send(msg)
                flash('A password reset code has been sent to your email address.', 'info')
                return redirect(url_for('forgot_password_verify', email=email))
            except Exception as e:
                flash(f'Failed to send reset email. Please check your Flask-Mail configuration and environment variables (EMAIL_USER, EMAIL_PASS). Error: {e}', 'danger')
                print(f"DEBUG: Email sending error: {e}")
        else:
            flash('If an account with that email exists, a password reset code has been sent.', 'info') 
            return redirect(url_for('forgot_password_verify', email=email)) 
            
    return render_template('forgot_password_request.html')

@app.route('/forgot_password/verify', methods=['GET', 'POST'])
def forgot_password_verify():
    email_from_args = request.args.get('email') 
    
    if request.method == 'POST':
        code = request.form.get('code')
        submitted_email = request.form.get('email')

        if not submitted_email:
            flash('Invalid request. Please start the password reset process again.', 'danger')
            return redirect(url_for('forgot_password_request'))

        code_data = password_reset_codes.get(submitted_email)

        if (code_data and 
            code_data['code'] == code and 
            dt.now() < code_data['expires_at'] and
            code_data['used'] == False):
            
            reset_token_for_password = secrets.token_urlsafe(32) 
            
            password_reset_codes[submitted_email]['reset_token'] = reset_token_for_password
            password_reset_codes[submitted_email]['used'] = True 

            flash('Code verified. You can now set your new password.', 'success')
            return redirect(url_for('forgot_password_reset', token=reset_token_for_password))
        else:
            flash('Invalid, expired, or already used code. Please try again or request a new one.', 'danger')
            if submitted_email in password_reset_codes:
                 if code_data and (code_data['code'] != code or dt.now() >= code_data['expires_at'] or code_data['used'] == True):
                     del password_reset_codes[submitted_email]
            
            return render_template('forgot_password_verify.html', email=submitted_email)

    if not email_from_args:
        flash('Invalid request. Please start the password reset process again.', 'danger')
        return redirect(url_for('forgot_password_request'))
        
    return render_template('forgot_password_verify.html', email=email_from_args)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def forgot_password_reset(token):
    email_for_token = None
    for email, data in password_reset_codes.items():
        if data.get('reset_token') == token and dt.now() < data.get('expires_at'):
            email_for_token = email
            break

    if not email_for_token:
        flash('Invalid or expired password reset link. Please try again.', 'danger')
        return redirect(url_for('forgot_password_request'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('forgot_password_reset.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('forgot_password_reset.html', token=token)

        user = User.query.filter_by(email=email_for_token).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit() 

            if email_for_token in password_reset_codes:
                del password_reset_codes[email_for_token] 

            flash('Your password has been reset successfully! Please log in with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error resetting password. User not found.', 'danger')
            return render_template('forgot_password_reset.html', token=token)

    return render_template('forgot_password_reset.html', token=token)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='test@example.com').first():
            test_user = User(username='testuser', email='test@example.com', dob='2000-01-01', phone=None,
                             password=generate_password_hash('password123'))
            db.session.add(test_user)
            db.session.commit()
            print("DEBUG: Default test user 'test@example.com' added to database.")

    app.run(debug=True)