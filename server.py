from os import path, getcwd
from sys import argv

from flask import Flask, render_template, session, redirect, send_from_directory
# from flask_cas import CAS
# from flask_cas import login
# from flask_cas import logout
# from flask_cas import login_required
# import logging

app = Flask(__name__)
# cas = CAS(app, '/cas')
# app.config['CAS_SERVER'] = 'https://fed.princeton.edu/cas/'
# app.config['CAS_AFTER_LOGIN'] = 'secure'

# DATABASE_URL = 'postgres://bgeduosfkxunua:79c8ea392b4ee24827466fffa6186fcd606e8fd61aed0f72474965c5058c00da@ec2-54-80-184-43.compute-1.amazonaws.com:5432/dbratmlm42smtt'

@app.route("/")
def main():
    return render_template("splash.html")

@app.route("/home")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')