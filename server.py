import os
from sys import argv
import urllib
import psycopg2

import flask
from flask import Flask, render_template, session, redirect, send_from_directory, request, url_for
from flask_cas import CAS, login_required, login, logout

from flask_wtf import FlaskForm
from forms import SignUpForm, RemoveForm

app = Flask(__name__)
app.secret_key = os.urandom(24)
cas = CAS(app)
app.config['CAS_SERVER'] = 'https://fed.princeton.edu/'
app.config['CAS_AFTER_LOGIN'] = '/home'
app.config['CAS_AFTER_LOGOUT'] = '/'

netid = ""

 
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
cursor.execute("INSERT INTO queue VALUES('test1','Test1','conc','2', '{1,3,5}')")
conn.commit()
cursor.execute("INSERT INTO queue VALUES('test2','Test2','debug','5', '{2,6}')")
conn.commit()
cursor.execute("INSERT INTO queue VALUES('test3','Test3','conc','10', '{3,4}')")
conn.commit()
cursor.execute("INSERT INTO queue VALUES('test4','Test4','conc','5', '{1,5}')")
conn.commit()

# Create database of instructors
# cursor.execute("DROP TABLE IF EXISTS instructors")
# conn.commit()
# cursor.execute("CREATE TABLE instructors (netid VARCHAR(50) NOT NULL PRIMARY KEY,)")
# conn.commit()
# cursor.execute("INSERT INTO instructors VALUES(%s)", ('kpetrino',))
# conn.commit()

# Create a key-value store of problem descriptions
problems = {1: 'Testing', 2: 'API', 3: 'Data Structures', 4: 'Algorithm', 5: 'Exception', 6: 'Getting Started'}

# Create a database for the problem descritions
# cursor.execute("DROP TABLE IF EXISTS problems")
# conn.commit()
# cursor.execute(
#     """
#     CREATE TABLE problems (
#         key INTEGER NOT NULL PRIMARY KEY,
#         val VARCHAR(50) NOT NULL,
#     )"""
# )
# conn.commit() 
# for k in problems:
#     cursor.execute("INSERT INTO problems VALUES(%d, %s)", (k, problems[k]))
#     conn.commit()


@app.route("/") 
def main():
    return render_template("splash.html")


@app.route("/home", methods=['GET','POST'])
@login_required
def home():
    netid = str(cas.username)
    form = SignUpForm()
    form2 = RemoveForm()

    # check if already in queue
    inqueue = True
    cursor.execute("SELECT netid FROM queue where netid = (%s)", (netid,))
    temp = cursor.fetchone()
    if temp == None:
        inqueue = False

    # form to join queue submitted
    if form.is_submitted() and not inqueue:
        queue = get_queue()
        result = request.form.to_dict()
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
            return render_template("index.html", mynetid=netid, form=form, form2=form2, queue=get_queue(), wait=get_wait(), match=match) 
    
    # form to remove self submitted
    # elif form2.is_submitted() and inqueue:
    #     result = request.form
    #     cursor.execute("DELETE FROM queue WHERE netid = (%s)", (netid,))
    #     conn.commit()
    
    return render_template("index.html", mynetid=netid, form=form, form2=form2, queue=get_queue(), wait=get_wait())

@app.route("/remove_self/<netid>")
def remove_self(netid):
    cursor.execute("DELETE FROM queue WHERE netid = (%s)", (netid,))
    conn.commit()
    return redirect(url_for('home'))


@app.route("/ta_portal", methods=['GET','POST'])
@login_required
def ta_portal():
    # form = RemoveForm()
    # if form.is_submitted():
    #     result = request.form
    #     cursor.execute("DELETE FROM queue WHERE netid = '%s'" % result["netid"])
    #     conn.commit()
    return render_template("ta_portal.html", queue=get_queue(), wait=get_wait())

@app.route("/remove/<netid>")
def remove(netid):
    cursor.execute("DELETE FROM queue WHERE netid = (%s)", (netid,))
    conn.commit()
    return redirect(url_for('ta_portal'))

@app.route("/remove_all")
def remove_all():
    queue = get_queue()
    for stu in queue:
        cursor.execute("DELETE FROM queue WHERE netid = (%s)", (stu[0],))
        conn.commit()
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