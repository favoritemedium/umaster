from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField
from wtforms import TextField, PasswordField, SelectField
from wtforms.validators import Required

class LoginForm(Form):
    domain = TextField('domain', validators=[Required(message="Domain is required.")])
    username = TextField('username', validators=[Required(message="Username is required.")])
    password = PasswordField('password', validators=[Required(message="Password is required.")])

class ChooseProjectForm(Form):
    project = SelectField('project', coerce=int, validators=[Required("Please choose a project.")])

class UploadForm(Form):
    csvfile = FileField('csvfile', validators=[Required("Please choose a file.")])

class FinalForm(Form):
    pass
