import os
from sys import argv
import urllib
import psycopg2

import flask
from flask import Flask, render_template, session, redirect, send_from_directory, request
from flask_cas import CAS, login_required, login, logout

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

app = Flask(__name__)
app.secret_key = os.urandom(24)
cas = CAS(app)
app.config['CAS_SERVER'] = 'https://fed.princeton.edu/'
app.config['CAS_AFTER_LOGIN'] = 'home'

DATABASE_URL = 'postgres://bgeduosfkxunua:79c8ea392b4ee24827466fffa6186fcd606e8fd61aed0f72474965c5058c00da@ec2-54-80-184-43.compute-1.amazonaws.com:5432/dbratmlm42smtt'
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
conn.commit()

cursor.execute("DROP TABLE IF EXISTS queue")
conn.commit()
cursor.execute(
    """
    CREATE TABLE queue (
        name VARCHAR(50) NOT NULL PRIMARY KEY,
        prob VARCHAR(50) NOT NULL,
        time INTEGER NOT NULL,
        descrip VARCHAR(100)
    )"""
)
conn.commit()


@app.route("/") 
def main():
    return render_template("splash.html")

class SignUpForm(FlaskForm):
    name = StringField('Name')
    prob = SelectField('Problem Type', choices=[('conc','Conceptual'), ('debug', 'Debugging')])
    time = SelectField('Estimated Time', choices=[('5', 'Quick'), ('9', 'Medium'), ('12', 'Long')])
    descrip = StringField('Description')
    submit = SubmitField('Submit')

@app.route("/home", methods=['GET','POST'])
@login_required
def home():
    form = SignUpForm()
    if form.is_submitted():
        result = request.form
        cursor.execute("INSERT INTO queue VALUES ('%s', '%s', %s. '%s'", (result("name"), result("prob"), result("time"), result("descrip")))
        conn.commit()
    cursor.execute("SELECT name, prob, descrip FROM queue")
    queue = cursor.fetchall()
    return render_template("index.html", netid=cas.username, form=form, queue=queue)


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')