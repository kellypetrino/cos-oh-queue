import os
from sys import argv
import urllib

import flask
from flask import Flask, render_template, session, redirect, send_from_directory
from flask_cas import CAS, login_required, login, logout

app = Flask(__name__)
app.secret_key = os.urandom(24)
cas = CAS(app)
app.config['CAS_SERVER'] = 'https://fed.princeton.edu/'
app.config['CAS_AFTER_LOGIN'] = 'home'

# DATABASE_URL = 'postgres://bgeduosfkxunua:79c8ea392b4ee24827466fffa6186fcd606e8fd61aed0f72474965c5058c00da@ec2-54-80-184-43.compute-1.amazonaws.com:5432/dbratmlm42smtt'
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# cursor = conn.cursor()
# conn.commit()

#https://github.com/cameronbwhite/flask-cas-demo/blob/master/app.py
# @app.route('/login/')
# def route_login():
#     if 'ticket' in flask.request.args:
#         flask.session['_cas_token'] = flask.request.args['ticket']

#     if '_cas_token' in flask.session:

#         if validate(flask.session['_cas_token']):
#             redirect_url = flask.url_for('home')
#         else:
#             redirect_url = create_cas_login_url(app.config['cas_server'])
#             del flask.session['_cas_token']
#     else:
#         redirect_url = create_cas_login_url(app.config['cas_server'])

#     app.logger.debug('Redirecting to: {}'.format(redirect_url))

#     return flask.redirect(redirect_url)

# @app.route('/logout/')
# def route_logout():
#     """
#     When the user accesses this route they are logged out.
#     """
#     if 'username' in flask.session:
#         del flask.session['username']
#     redirect_url = create_cas_logout_url(app.config['cas_server'])
#     app.logger.debug('Redirecting to: {}'.format(redirect_url))
#     return flask.redirect(redirect_url)

# def create_cas_login_url(cas_url):
#     service_url = urllib.parse.quote(
#         flask.url_for('route_login',_external=True))
#     return urllib.parse.urljoin(
#         cas_url, 
#         '/cas/?service={}'.format(service_url))

# def create_cas_logout_url(cas_url):
#     url = urllib.parse.quote(flask.url_for('route_login', _external=True))
#     return urllib.parse.urljoin(
#         cas_url,
#         '/cas/logout?url={}'.format(url))

# def create_cas_validate_url(cas_url, ticket):
#     service_url = urllib.parse.quote(
#         flask.url_for('route_login',_external=True))
#     ticket = urllib.parse.quote(ticket)
#     return urllib.parse.urljoin(
#         cas_url,
#         '/cas/validate?service={}&ticket={}'.format(service_url, ticket))

# def validate(ticket):
#     """
#     Will attempt to validate the ticket. If validation fails False 
#     is returned. If validation is successful then True is returned 
#     and the validated username is saved in the session under the 
#     key `username`.
#     """

#     app.logger.debug("validating token {}".format(ticket))

#     cas_validate_url = create_cas_validate_url(
#         app.config['cas_server'], ticket)
    
#     app.logger.debug("Making GET request to {}".format(
#         cas_validate_url))

#     try:
#         (isValid, username) = urllib.request.urlopen(cas_validate_url).readlines()
#         isValid = True if isValid.strip() == 'yes' else False
#         username = username.strip()
#     except ValueError:
#         app.logger.error("CAS returned unexpected result")
#         isValid = False

#     if isValid:
#         app.logger.debug("valid")
#         flask.session['username'] = username
#     else:
#         app.logger.debug("invalid")

#     return isValid

@app.route("/")
@login_required
def main():
    return "SPLASH PAGE GOES HERE"
    # return render_template("splash.html")

@app.route("/home")
def home():
    return "yikes %s" % cas.username 
    # return render_template("index.html")


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=PORT, host='0.0.0.0')