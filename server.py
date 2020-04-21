import os
from sys import argv
import urllib
import psycopg2

import flask
from flask import Flask, render_template, session, redirect, send_from_directory, request
from flask_cas import CAS, login_required, login, logout

from flask_wtf import FlaskForm
from forms import SignUpForm, RemoveForm

app = Flask(__name__)
app.secret_key = os.urandom(24)
cas = CAS(app)
app.config['CAS_SERVER'] = 'https://fed.princeton.edu/'
app.config['CAS_AFTER_LOGIN'] = '/home'
app.config['CAS_AFTER_LOGOUT'] = '/'

 
# conn = psycopg2.connect(host="localhost",database="ohlocal", user="postgres", password="sqlpass")
DATABASE_URL = 'postgres://bgeduosfkxunua:79c8ea392b4ee24827466fffa6186fcd606e8fd61aed0f72474965c5058c00da@ec2-54-80-184-43.compute-1.amazonaws.com:5432/dbratmlm42smtt'
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

cursor = conn.cursor()
conn.commit()

# Create table to store the current queue of students
cursor.execute("DROP TABLE IF EXISTS queue")
conn.commit()
cursor.execute(
    """
    CREATE TABLE queue (
        netid VARCHAR(50) NOT NULL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        prob VARCHAR(50) NOT NULL,
        time VARCHAR(10) NOT NULL,
        descrip VARCHAR(100)
    )"""
)
conn.commit()

# Create a key-value store of problem descriptions
problems = {1: 'Testing', 2: 'API', 3: 'Data Structures', 4: 'Algorithm', 5: 'Exception', 6: 'Getting Started'}


@app.route("/") 
def main():
    return render_template("splash.html")


@app.route("/home", methods=['GET','POST'])
# @login_required
def home():
    form = SignUpForm()
    form2 = RemoveForm()
    if form.is_submitted():
        queue = get_queue()
        result = request.form.to_dict()
        # print(type(result))
        # print(result)
        # print(form.descrip.data)
        # print(type(form.descrip.data))
        cursor.execute("INSERT INTO queue VALUES (%s, %s, %s, %s, %s)", (cas.username, result["name"], result["prob"], result["time"], form.descrip.data))
        conn.commit()
        if len(queue) > 0: 
            sim = 0
            match = queue[0]
            for stu in queue:
                sim_temp = jaccard(result, stu)
                if sim_temp > sim:
                    sim = sim_temp
                    match = stu
            # print(match)
            # print(type(match))
            # print(type(match[3]))
            return render_template("index.html", form=form, form2=form2, queue=get_queue(), wait=get_wait(), match=match) 
    elif form2.is_submitted():
        result = request.form
        cursor.execute("DELETE FROM queue WHERE netid = '%s'" % cas.username)
        conn.commit()
    return render_template("index.html", form=form, form2=form2, queue=get_queue(), wait=get_wait())


@app.route("/ta_portal", methods=['GET','POST'])
@login_required
def ta_portal():
    form = RemoveForm()
    if form.is_submitted():
        result = request.form
        cursor.execute("DELETE FROM queue WHERE name = '%s'" % result["name"])
        conn.commit()
    return render_template("ta_portal.html", form=form, queue=get_queue(), wait=get_wait())

def get_queue():
    cursor.execute("SELECT name, prob, time, descrip FROM queue")
    queue = cursor.fetchall()
    return queue

def get_wait():
    queue = get_queue()
    wait = 0
    for stu in queue:
        wait = wait + int(stu[2])
    return wait

def jaccard(a, b):
    cp = 0
    pa = 0
    ap = 0
    for i in problems:
        if str(i) in a["descrip"]:
            if str(i) in b[3]:
                cp = cp + 1
            else:
                pa = pa + 1
        elif str(i) in b[3]:
            ap = ap + 1
    sim = cp / (cp + pa + ap)
    return sim

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')