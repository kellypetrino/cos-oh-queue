from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, HiddenField, SelectMultipleField

class SignUpForm(FlaskForm):
    name = StringField('Name')
    prob = SelectField('Problem Type', choices=[('conc','Conceptual'), ('debug', 'Debugging')])
    time = SelectField('Estimated Time', choices=[('5', 'Quick'), ('9', 'Medium'), ('12', 'Long')])
    descrip = SelectMultipleField('Description', choices=[('1', 'Testing'), ('2', 'API'), ('3', 'Data Structure'), ('4', 'Algorithm'), ('5', 'Exception'), ('6', 'Getting Started')])
    submit = SubmitField('Join Queue')

class RemoveForm(FlaskForm):
    netid = HiddenField('netid')
    submit = SubmitField('X')