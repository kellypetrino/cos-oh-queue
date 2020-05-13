import os
from sys import argv
import urllib
import psycopg2

import flask
from flask import Flask, render_template, session, redirect, send_from_directory, request, url_for
from flask_cas import CAS, login_required, login, logout

from flask_wtf import FlaskForm
from forms import SignUpForm, RemoveForm, AddTAForm

app = Flask(__name__)
app.secret_key = os.urandom(24)
cas = CAS(app)
app.config['CAS_SERVER'] = 'https://fed.princeton.edu/'
app.config['CAS_AFTER_LOGIN'] = '/home'
app.config['CAS_AFTER_LOGOUT'] = '/'

netid = ""

matches = {'Test1':'Test1', 'Test2':'Test2', 'Test3':'Test3', 'Test4':'Test4'}

 
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

# add test students
cursor.execute("INSERT INTO queue VALUES('test1','Test1','Conceptual','5', '{API,Data Structures,Getting Started}')")
conn.commit()
cursor.execute("INSERT INTO queue VALUES('test2','Test2','Conceptual','2', '{Testing,API,Getting Started}')")
conn.commit()
cursor.execute("INSERT INTO queue VALUES('test3','Test3','Debugging','5', '{Testing,Exception}')")
conn.commit()
cursor.execute("INSERT INTO queue VALUES('test4','Test4','Conceptual','5', '{Testing,Getting Started}')")
conn.commit()

# Create database of instructors
# cursor.execute("DROP TABLE IF EXISTS instructors")
# conn.commit()
# cursor.execute(
#     """
#     CREATE TABLE instructors (
#         netid VARCHAR(50) NOT NULL PRIMARY KEY
#     )"""
# )
# conn.commit()
# cursor.execute("INSERT INTO instructors VALUES(%s)", ('kpetrino',))
# conn.commit()

# Create a key-value store of problem descriptions
problems = ['Testing','API','Data Structures','Algorithm','Exception','Getting Started']

# Create a database for the problem descritions
# cursor.execute("DROP TABLE IF EXISTS problems")
# conn.commit()
# cursor.execute(
#     """
#     CREATE TABLE problems (
#         key INTEGER NOT NULL PRIMARY KEY,
#         val VARCHAR(50) NOT NULL
#     )"""
# )
# conn.commit() 
# for k in problems:
#     cursor.execute("INSERT INTO problems VALUES(%d, %s)", (k, problems[k]))
#     conn.commit()


@app.route("/") 
def main():
    return render_template("splash.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/home", methods=['GET','POST'])
@login_required
def home():
    netid = str(cas.username)

    # redirect instructors to ta portal
    cursor.execute("SELECT netid FROM instructors WHERE netid = (%s)", (netid,))
    isInstructor = True
    if cursor.fetchone() == None:
        isInstructor = False
    if isInstructor and (netid != 'kpetrino') and (netid != 'rfish'):
        return redirect(url_for('ta_portal'))

    form = SignUpForm()

    # check if already in queue
    inqueue = True
    cursor.execute("SELECT netid FROM queue where netid = (%s)", (netid,))
    temp = cursor.fetchone()
    if temp == None:
        inqueue = False
    else: 
        match = matches[netid]
        return render_template("index.html", mynetid=netid, form=form, queue=get_queue(), wait=get_wait(), match=match) 


    # form to join queue submitted
    if form.is_submitted() and not inqueue:
        queue = get_queue()
        result = request.form.to_dict()
        result["descrip"] = form.descrip.data
        cursor.execute("INSERT INTO queue VALUES (%s, %s, %s, %s, %s)", (netid, form.name.data, form.prob.data, form.time.data, form.descrip.data))
        conn.commit()
        # get match 
        if len(queue) > 0: 
            sim = 0
            match = queue[0]
            for stu in queue:
                sim_temp = jaccard(result, stu)
                if sim_temp > sim:
                    sim = sim_temp
                    match = stu
            matches[netid] = match
            return render_template("index.html", mynetid=netid, form=form, queue=get_queue(), wait=get_wait(), match=match) 
        else:
            matches[netid] = netid
    
    return render_template("index.html", mynetid=netid, form=form, queue=get_queue(), wait=get_wait())

@app.route("/remove_self/<netid>")
def remove_self(netid):
    cursor.execute("DELETE FROM queue WHERE netid = (%s)", (netid,))
    conn.commit()
    return redirect(url_for('home'))


@app.route("/ta_portal", methods=['GET','POST'])
@login_required
def ta_portal():
    # redirect students to student home
    cursor.execute("SELECT netid FROM instructors WHERE netid = (%s)", (netid,))
    if cursor.fetchone() == None:
        return redirect(url_for('home'))

    form = AddTAForm()
    if form.is_submitted():
        cursor.execute("INSERT INTO instructors VALUES (%s)", (form.netid.data,))
    return render_template("ta_portal.html", queue=get_queue(), wait=get_wait(), form=form)

@app.route("/remove/<netid>")
def remove(netid):
    cursor.execute("DELETE FROM queue WHERE netid = (%s)", (netid,))
    conn.commit()
    # del matches[netid]
    return redirect(url_for('ta_portal'))

@app.route("/remove_all")
def remove_all():
    queue = get_queue()
    for stu in queue:
        cursor.execute("DELETE FROM queue WHERE netid = (%s)", (stu[0],))
        conn.commit()
        # del matches[stu[0]]
    return redirect(url_for('ta_portal'))

def get_queue():
    cursor.execute("SELECT netid, name, prob, time, descrip FROM queue")
    queue = cursor.fetchall()
    return queue

def get_wait():
    queue = get_queue()
    wait = 0
    for stu in queue:
        wait = wait + int(stu[3])
    return wait

def jaccard(a, b):
    cp = 0
    pa = 0
    ap = 0
    print(a)
    print(b)
    for i in problems:
        if str(i) in a["descrip"]:
            if str(i) in b[4]:
                cp = cp + 1
            else:
                pa = pa + 1
        elif str(i) in b[4]:
            ap = ap + 1
    sim = cp / (cp + pa + ap)
    print(sim)
    return sim

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')