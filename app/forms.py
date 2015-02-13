from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField
from wtforms import TextField, PasswordField, SelectField
from wtforms.validators import Required

class LoginForm(Form):
    domain = TextField('domain', validators=[Required()])
    username = TextField('username', validators=[Required()])
    password = PasswordField('password', validators=[Required()])

class ChooseProjectForm(Form):
    project = SelectField('project', coerce=int, validators=[Required()])

class UploadForm(Form):
    csvfile = FileField('csvfile', validators=[Required()])

class FinalForm(Form):
    pass
