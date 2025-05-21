from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets # For generating simple reset codes (NOT for secure tokens in real apps without more context)
import datetime # For handling code expiration

# --- OPTIONAL: For loading environment variables from a .env file ---
# If you created a .env file for email credentials, uncomment the next two lines:
from dotenv import load_dotenv
load_dotenv()

# --- Flask-Mail Imports and Configuration (Requires installation: pip install Flask-Mail) ---
from flask_mail import Mail, Message

app = Flask(__name__)
# IMPORTANT: Replace with a strong, static secret key in production.
# This is used for session management and flash messages.
app.secret_key = os.urandom(24) 

# --- Flask-Mail Configuration ---
# IMPORTANT: Replace with your actual email server settings if not Gmail,
# and ensure MAIL_USERNAME/MAIL_PASSWORD are set via environment variables.
app.config['MAIL_SERVER'] = 'smtp.gmail.com' # Example for Gmail. Use your provider's SMTP server.
app.config['MAIL_PORT'] = 587 # Typically 587 for TLS, or 465 for SSL.
app.config['MAIL_USE_TLS'] = True # Set to False if using SSL (port 465)
app.config['MAIL_USE_SSL'] = False # Set to True if using SSL (port 465)
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') # Get from environment variable (from your .env file)
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') # Get from environment variable (from your .env file / Gmail App Password!)
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER') # Your sending email address

mail = Mail(app)

# --- Dummy User Database (In-memory list, NOT for production!) ---
# In a real application, you would connect to a proper database (e.g., SQLAlchemy with SQLite/PostgreSQL).
users = [] 

# --- Temporarily store password reset codes/tokens (NOT for production!) ---
# In a real application, these would be stored in a database, associated with the user,
# with expiration times, and should be single-use.
# Format: {email: {'code': 'XXXXXX', 'expires_at': datetime_obj, 'reset_token': 'secure_token_for_step_3', 'used': False}}
password_reset_codes = {}

@app.route('/')
def home():
    # Example movie data for the carousel (replace with real data from a DB)
    movies = [
        {'title': 'Movie Title 1', 'image_filename': 'movie1.jpg'},
        {'title': 'Movie Title 2', 'image_filename': 'movie2.jpg'},
        {'title': 'Movie Title 3', 'image_filename': 'movie3.jpg'},
        {'title': 'Movie Title 4', 'image_filename': 'movie4.jpg'},
        {'title': 'Movie Title 5', 'image_filename': 'movie5.jpg'}
    ]
    return render_template('home.html', movies=movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier'] # Can be email or phone
        password = request.form['password']

        user = None
        for u in users:
            if u['email'] == identifier or u.get('phone') == identifier:
                user = u
                break

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
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
        phone = request.form.get('phone') # Optional
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic validation
        if not username or not email or not dob or not password or not confirm_password:
            flash('All fields marked with * are required.', 'danger')
            return render_template('signup.html', form_data=request.form)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html', form_data=request.form)

        if len(password) < 6: # Minimum password length
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('signup.html', form_data=request.form)

        # Check if username or email already exists
        for user in users:
            if user['username'] == username:
                flash('Username already taken.', 'danger')
                return render_template('signup.html', form_data=request.form)
            if user['email'] == email:
                flash('Email already registered.', 'danger')
                return render_template('signup.html', form_data=request.form)

        hashed_password = generate_password_hash(password)
        new_user = {
            'username': username,
            'email': email,
            'dob': dob,
            'phone': phone,
            'password': hashed_password
        }
        users.append(new_user)
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

# --- NEW FORGOT PASSWORD ROUTES ---

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password_request():
    """
    Step 1: User requests a password reset by providing their email.
    A reset code is generated and emailed.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        
        # In a real app, perform a database lookup for the email
        user_exists = any(u['email'] == email for u in users) 

        if user_exists:
            # --- SECURITY WARNING: Simplified token generation for demo ONLY ---
            # In a real app, use a robust, cryptographically secure library like `itsdangerous`
            # or a dedicated token management system. Store tokens securely in a database
            # with proper expiration and single-use flags. Do NOT use simple integers/short strings.
            reset_code = secrets.token_urlsafe(6) # Generates a random string (e.g., 'abc-123')
            # For a 6-digit numeric code, you could generate: str(random.randint(100000, 999999))

            expires_at = datetime.datetime.now() + datetime.timedelta(minutes=15) # Code valid for 15 minutes

            # Store the code temporarily (INSECURE FOR PROD: use DB!)
            password_reset_codes[email] = {'code': reset_code, 'expires_at': expires_at, 'used': False}

            # --- EMAIL SENDING LOGIC ---
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
                print(f"DEBUG: Email sending error: {e}") # For debugging on the server console
        else:
            # For security, always give a generic message to prevent email enumeration
            flash('If an account with that email exists, a password reset code has been sent.', 'info') 
            # Still redirect to the verify page to maintain consistent flow
            return redirect(url_for('forgot_password_verify', email=email)) # Pass email to verify page
            
    return render_template('forgot_password_request.html')

@app.route('/forgot_password/verify', methods=['GET', 'POST'])
def forgot_password_verify():
    """
    Step 2: User enters the code received in their email.
    If the code is correct and not expired, they are redirected to set a new password.
    """
    email_from_args = request.args.get('email') # Get email from URL query parameter (from previous step)
    
    if request.method == 'POST':
        code = request.form.get('code')
        submitted_email = request.form.get('email') # Get email from hidden input in form

        # Ensure we have an email to check against
        if not submitted_email:
            flash('Invalid request. Please start the password reset process again.', 'danger')
            return redirect(url_for('forgot_password_request'))

        code_data = password_reset_codes.get(submitted_email)

        if (code_data and 
            code_data['code'] == code and 
            datetime.datetime.now() < code_data['expires_at'] and
            code_data['used'] == False): # Check if code hasn't been used yet for *this step*
            
            # Code is correct and not expired. Generate a secure token for the next step (actual reset).
            # This token is passed via the URL to the reset page and is different from the emailed code.
            reset_token_for_password = secrets.token_urlsafe(32) 
            
            # Update the stored code to include this reset_token and mark it as used for *this verification*
            # In a real app, this would update your database entry for the token
            password_reset_codes[submitted_email]['reset_token'] = reset_token_for_password
            password_reset_codes[submitted_email]['used'] = True # Mark the emailed code as used for verification

            flash('Code verified. You can now set your new password.', 'success')
            return redirect(url_for('forgot_password_reset', token=reset_token_for_password))
        else:
            flash('Invalid, expired, or already used code. Please try again or request a new one.', 'danger')
            # Optional: Clean up expired/invalid codes from the temporary storage (or DB)
            if submitted_email in password_reset_codes:
                 # Only delete if it's genuinely invalid/expired or wrong code entered for valid email
                 if code_data and (code_data['code'] != code or datetime.datetime.now() >= code_data['expires_at'] or code_data['used'] == True):
                     del password_reset_codes[submitted_email]
            
            # Redirect back to the verify page with the original email to allow re-entry
            return render_template('forgot_password_verify.html', email=submitted_email)

    # If it's a GET request, ensure email is present from previous redirect
    if not email_from_args:
        flash('Invalid request. Please start the password reset process again.', 'danger')
        return redirect(url_for('forgot_password_request'))
        
    return render_template('forgot_password_verify.html', email=email_from_args)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def forgot_password_reset(token):
    """
    Step 3: User sets their new password using the unique token.
    """
    # In a real app, look up the token in your database to find the associated user and ensure it's valid.
    # The token should be single-use and time-limited.
    email_for_token = None
    for email, data in password_reset_codes.items():
        # Check if the 'reset_token' matches and is not expired (using the 'expires_at' from the original code)
        if data.get('reset_token') == token and datetime.datetime.now() < data.get('expires_at'):
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

        # --- UPDATE USER PASSWORD IN DATABASE ---
        # In a real application, you would:
        # 1. Look up the user in your database using `email_for_token`.
        # 2. Hash the `new_password` using generate_password_hash().
        # 3. Update the user's password in the database.
        # 4. CRITICAL: Invalidate (delete or mark as used) the reset `token` from your database to prevent reuse.
        #    Here, we'll remove the entire entry from our dummy dictionary for simplicity after successful reset.
        
        user_found_and_updated = False
        for user in users:
            if user['email'] == email_for_token:
                user['password'] = generate_password_hash(new_password)
                user_found_and_updated = True
                break

        if user_found_and_updated:
            # IMPORTANT: After successful password reset, invalidate the token/code
            if email_for_token in password_reset_codes:
                del password_reset_codes[email_for_token] 

            flash('Your password has been reset successfully! Please log in with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error resetting password. User not found or token issue.', 'danger')
            return render_template('forgot_password_reset.html', token=token)

    return render_template('forgot_password_reset.html', token=token)

if __name__ == '__main__':
    # Initial dummy user for testing if the users list is empty
    # This user (test@example.com / password123) will exist only if app.py starts with no users.
    if not users:
        users.append({
            'username': 'testuser',
            'email': 'test@example.com',
            'dob': '2000-01-01',
            'phone': None,
            'password': generate_password_hash('password123')
        })
        print("DEBUG: Dummy user 'testuser' (test@example.com / password123) added for testing.")

    app.run(debug=True) # Run in debug mode during development