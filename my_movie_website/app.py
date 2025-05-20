# app.py
from flask import Flask, render_template # Keep imports minimal for now

app = Flask(__name__)

# Basic configuration
app.secret_key = 'your_very_secret_key_here' 

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login') # Added /login route explicitly for clarity, though / handles it
def login():
    return render_template('login.html')

@app.route('/signup') # NEW ROUTE for the signup page
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)