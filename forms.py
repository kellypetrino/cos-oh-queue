from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

class SignUpForm(FlaskForm):
    name = StringField('Name')
    prob_type = SelectField('Type', choices=[('conc','Conceptual'), ('debug', 'Debugging')])
    time = SelectField('Estimated Time', choices=[('5', 'Quick'), ('9', 'Medium'), ('12', 'Long')])
    descrip = StringField('Description')
    submit = SubmitField('Submit')
