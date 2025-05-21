# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.models import db, User, Movie
import os
import re
from sqlalchemy import inspect
from sqlalchemy_utils import database_exists, create_database

app = Flask(__name__)

# --- Configuration ---
app.secret_key = 'your_very_secret_key_here_change_this_in_production'
basedir = os.path.abspath(os.path.dirname(__file__))

# --- Database for Users ---
USER_DB_NAME = 'login_information.db'
user_db_path = os.path.join(basedir, 'database', USER_DB_NAME)
user_db_uri = 'sqlite:///' + user_db_path

# --- Database for Movies ---
MOVIE_DB_NAME = 'movies_data.db' 
movie_db_path = os.path.join(basedir, 'database', MOVIE_DB_NAME)
movie_db_uri = 'sqlite:///' + movie_db_path

# Ensure the 'database' directory exists
os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)

# Configure SQLAlchemy for the primary (User) database and the secondary (Movies) database
app.config['SQLALCHEMY_DATABASE_URI'] = user_db_uri # Default bind for User model
app.config['SQLALCHEMY_BINDS'] = {
    'movies': movie_db_uri # 'movies' bind for Movie model
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recommended to suppress warnings

# Initialize SQLAlchemy with the app
db.init_app(app)

# --- Create Database Tables and Seed Movie Data (if they don't exist) ---
with app.app_context():
    # Create User database tables (default bind)
    print(f"DEBUG: Initializing User DB: {user_db_path}")
    db.create_all() # This creates tables for the default bind (User model)
    inspector_user = inspect(db.engine)
    print(f"DEBUG: Tables in User DB: {inspector_user.get_table_names()}")

    # Create Movie database tables and seed data if needed
    print(f"DEBUG: Initializing Movie DB: {movie_db_path}")
    if not database_exists(movie_db_uri):
        create_database(movie_db_uri)
        print(f"DEBUG: Created new Movie database: {movie_db_uri}")
    
    # Create tables for the 'movies' bind
    db.create_all(bind_key='movies')
    inspector_movie = inspect(db.get_engine(app, bind='movies'))
    movie_tables = inspector_movie.get_table_names()
    print(f"DEBUG: Tables in Movie DB: {movie_tables}")

    # Seed initial movie data if the 'movie' table is empty
    if 'movie' in movie_tables and db.session.query(Movie).count() == 0:
        print("DEBUG: Seeding initial movie data...")
        # --- Movie data with image_filename for static files ---
        sample_movies = [
            {'title': 'The Shawshank Redemption', 'image_filename': 'movie1.jpg'},
            {'title': 'The Godfather', 'image_filename': 'movie2.jpg'},
            {'title': 'The Dark Knight', 'image_filename': 'movie3.jpg'},
            {'title': 'Pulp Fiction', 'image_filename': 'movie4.jpg'},
            {'title': 'The Lord of the Rings', 'image_filename': 'movie5.jpg'},
            {'title': 'Forrest Gump', 'image_filename': 'movie6.jpg'},
            {'title': 'Inception', 'image_filename': 'movie7.jpg'},
            {'title': 'Fight Club', 'image_filename': 'movie8.jpg'},
            {'title': 'The Matrix', 'image_filename': 'movie9.jpg'},
            {'title': 'Interstellar', 'image_filename': 'movie10.jpg'},
            {'title': 'Gladiator', 'image_filename': 'movie11.jpg'},
            {'title': 'Inglourious Basterds', 'image_filename': 'movie12.jpg'},
            {'title': 'Django Unchained', 'image_filename': 'movie13.jpg'},
            {'title': 'Spirited Away', 'image_filename': 'movie14.jpg'},
            {'title': 'Parasite', 'image_filename': 'movie15.jpg'},
            {'title': 'Avengers: Endgame', 'image_filename': 'movie16.jpg'},
            {'title': 'Whiplash', 'image_filename': 'movie17.jpg'},
            {'title': 'La La Land', 'image_filename': 'movie18.jpg'},
            {'title': 'Joker', 'image_filename': 'movie19.jpg'},
            {'title': 'Spider-Man: Into the Spider-Verse', 'image_filename': 'movie20.jpg'},
            {'title': 'Your Name.', 'image_filename': 'movie21.jpg'},
            {'title': 'Coco', 'image_filename': 'movie22.jpg'},
            {'title': 'Guardians of the Galaxy', 'image_filename': 'movie23.jpg'},
            {'title': 'Deadpool', 'image_filename': 'movie24.jpg'},
            {'title': 'Arrival', 'image_filename': 'movie25.jpg'},
            {'title': 'Blade Runner 2049', 'image_filename': 'movie26.jpg'},
            {'title': 'Mad Max: Fury Road', 'image_filename': 'movie27.jpg'},
            {'title': "Schindler's List", 'image_filename': 'movie28.jpg'},
            {'title': 'Birdman', 'image_filename': 'movie29.jpg'},
            {'title': 'Hacksaw Ridge', 'image_filename': 'movie30.jpg'}
        ]
        for movie_data in sample_movies:
            # Check if movie already exists to prevent duplicates on re-run
            existing_movie = Movie.query.filter_by(image_filename=movie_data['image_filename']).first()
            if not existing_movie:
                new_movie = Movie(**movie_data)
                db.session.add(new_movie)
        db.session.commit()
        print("DEBUG: Movie data seeded successfully.")
    elif 'movie' in movie_tables:
        print(f"DEBUG: Movie table already contains {db.session.query(Movie).count()} entries. Skipping seeding.")
    else:
        print("DEBUG: 'movie' table not found in Movie DB. Something might be wrong with bind setup or create_all(bind_key='movies').")


# --- Validation Helper Functions ---

def is_valid_email(email):
    """Basic regex for email validation."""
    return re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def is_valid_nz_phone(phone):
    """
    Validates a New Zealand phone number.
    Accepts formats like:
    +64211234567 (with or without spaces/hyphens)
    0211234567 (with or without spaces/hyphens)
    """
    if not phone:
        return False

    cleaned_phone = phone.replace(' ', '').replace('-', '')

    # Regex for NZ phone numbers
    nz_phone_regex = r"^(\+64|0)(21|22|27|20|24|28|29)\d{6,8}$|^(\+64|0)([34679])\d{7,8}$"
    
    return re.fullmatch(nz_phone_regex, cleaned_phone)

# --- Routes ---

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('welcome'))
    return redirect(url_for('home'))

@app.route('/home')
def home():
    if 'username' in session:
        return redirect(url_for('welcome'))
    movies = Movie.query.all()
    return render_template('home.html', movies=movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('welcome'))

    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        if not identifier or not password:
            flash('Please fill in both fields.', 'danger')
            return render_template('login.html', identifier=identifier)

        user = None
        
        if is_valid_email(identifier):
            user = User.query.filter_by(email=identifier).first()
        elif is_valid_nz_phone(identifier):
            user = User.query.filter_by(phone=identifier).first()
        else:
            flash('Please enter a valid email or New Zealand phone number.', 'danger')
            return render_template('login.html', identifier=identifier)


        if user and user.check_password(password):
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('Invalid email/phone number or password. Please try again.', 'danger')
            return render_template('login.html', identifier='')


    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('welcome'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        dob = request.form.get('dob')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        error_messages = []
        
        form_data = {
            'username': username,
            'email': email,
            'dob': dob,
            'phone': phone,
        }

        # --- Server-side validation ---
        if not all([username, email, dob, password, confirm_password]):
            error_messages.append("All required fields must be filled in.")
        else:
            if password != confirm_password:
                error_messages.append("Passwords do not match.")

            if User.query.filter_by(username=username).first():
                error_messages.append(f"Username '{username}' is already taken. Please choose another.")


            if not is_valid_email(email):
                error_messages.append("Invalid email format. Please use a valid email address.")
            elif User.query.filter_by(email=email).first():
                error_messages.append(f"Email address '{email}' is already registered.")
            
            if phone:
                if not is_valid_nz_phone(phone):
                    error_messages.append("Invalid New Zealand phone number format. Please ensure it starts with '+64' or '0' and is a valid length (e.g., +64211234567 or 0211234567).")
                elif User.query.filter_by(phone=phone).first():
                    error_messages.append(f"Phone number '{phone}' is already registered.")


            if len(password) < 8:
                error_messages.append("Password must be at least 8 characters long.")

        if error_messages:
            for error in error_messages:
                flash(error, 'danger')
            return render_template('signup.html', **form_data)

        new_user = User(
            username=username,
            email=email,
            dob=dob,
            phone=phone if phone else None
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating user: {e}")
            flash('An error occurred while creating your account. Please try again.', 'danger')
            return render_template('signup.html', **form_data)

    return render_template('signup.html')

@app.route('/welcome')
def welcome():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('home'))
    
    username = session.get('username')
    flash("Welcome back! You're logged in. Here's a placeholder for your main movie page.", 'info')
    return redirect(url_for('placeholder_main_page'))

@app.route('/main')
def placeholder_main_page():
    if 'username' not in session:
        flash('Please log in to access the main content.', 'warning')
        return redirect(url_for('home'))
    return render_template('placeholder_main.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)