from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.models import db, User
import os
import re
from sqlalchemy import inspect

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here_change_this_in_production'

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'login_information.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)
db.init_app(app)

with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    print(f"Tables in DB: {inspector.get_table_names()}")

def is_valid_email(email):
    return re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def is_valid_nz_phone(phone):
    if not phone:
        return False
    cleaned = phone.replace(' ', '').replace('-', '')
    return re.fullmatch(r"^(\+64|0)(21|22|27|20|24|28|29)\d{6,8}$|^(\+64|0)([34679])\d{7,8}$", cleaned)

@app.route('/')
def index():
    return redirect(url_for('login'))

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

        form_data = {'username': username, 'email': email, 'dob': dob, 'phone': phone}
        errors = []

        if not all([username, email, dob, password, confirm_password]):
            errors.append("All required fields must be filled in.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append(f"Username '{username}' is already taken.")
        if not is_valid_email(email):
            errors.append("Invalid email format.")
        elif User.query.filter_by(email=email).first():
            errors.append(f"Email '{email}' is already registered.")
        if phone:
            if not is_valid_nz_phone(phone):
                errors.append("Invalid New Zealand phone number.")
            elif User.query.filter_by(phone=phone).first():
                errors.append(f"Phone number '{phone}' is already registered.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('signup.html', **form_data)

        new_user = User(username=username, email=email, dob=dob, phone=phone if phone else None)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/welcome')
def welcome():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('welcome.html', username=session['username'])

@app.route('/account')
def account():
    if 'username' not in session:
        flash('Please log in to access your account.', 'warning')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    return render_template('account.html', user=user)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
