import os
from sys import argv

from flask import Flask, render_template, session, redirect, send_from_directory
from flask_cas import CAS, login_required

app = Flask(__name__)
app.secret_key = os.urandom(24)
cas = CAS(app, '/cas')
app.config['CAS_SERVER'] = 'https://fed.princeton.edu/cas/'
app.config['CAS_AFTER_LOGIN'] = 'home'

# DATABASE_URL = 'postgres://bgeduosfkxunua:79c8ea392b4ee24827466fffa6186fcd606e8fd61aed0f72474965c5058c00da@ec2-54-80-184-43.compute-1.amazonaws.com:5432/dbratmlm42smtt'

@app.route("/")
@login_required
def route_root():
    return "Testing %s" % cas.username

@app.route("/splash")
def main():
    return "SPLASH PAGE GOES HERE"
    # return render_template("splash.html")

@app.route("/home")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')