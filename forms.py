from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, HiddenField, SelectMultipleField

class SignUpForm(FlaskForm):
    name = StringField('Name')
    prob = SelectField('Problem Type', choices=[('Conceptual','Conceptual'), ('Debugging', 'Debugging')])
    time = SelectField('Estimated Time', choices=[('2', 'Quick'), ('5', 'Medium'), ('10', 'Long')])
    descrip = SelectMultipleField('Description', choices=[(' Testing ', 'Testing'), ('API', 'API'), (' Data Structures ', 'Data Structure'), (' Algorithm ', 'Algorithm'), ('  Exception ', 'Exception'), (' Getting Started ', 'Getting Started')])
    submit = SubmitField('Join Queue')
    remove = SubmitField('X')

class RemoveForm(FlaskForm):
    netid = HiddenField('netid')
    submit = SubmitField('X')

class AddTAForm(FlaskForm):
    netid = StringField('NetID')
    submit = SubmitField('Add Instructor')