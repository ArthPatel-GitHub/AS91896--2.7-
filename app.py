# app.py
from flask import Flask, render_template

app = Flask(__name__)

# Basic configuration (secret_key is important, but for this first commit,
# we'll keep it simple and add DB config later)
app.secret_key = 'your_very_secret_key_here' 

@app.route('/')
def index():
    return render_template('login.html') # A placeholder for now

if __name__ == '__main__':
    app.run(debug=True)