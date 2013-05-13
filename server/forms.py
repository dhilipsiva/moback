from wtforms.form import Form
from wtforms.validators import length, Email, required,\
        NumberRange
from wtforms.fields import TextField


class AuthForm(Form):
    access_token = TextField(u'access_token',
            validators=[required(), length(min=36, max=36)])
    person_id = TextField(u'person_id',
            validators=[required()])


class UserPassForm(Form):
    username = TextField(u'username',
            validators=[required(), length(min=4, max=30)])
    password = TextField(u'password',
            validators=[required(), length(min=6, max=20)])


class SignupForm(UserPassForm):
    id = TextField(u'person_id')
    firstname = TextField(u'firstname',
            validators=[required(), length(min=4, max=35)])
    lastname = TextField(u'lastname',
            validators=[required(), length(min=4, max=35)])
    email = TextField(u'email',
            validators=[required(), Email(),
                length(min=6, max=100)])


class PointForm(AuthForm):
    id = TextField(u'id',
            validators=[required(), length(min=36, max=36)])
    score = TextField(u'score',
            validators=[required(), NumberRange(min=0)])
    score_time = TextField(u'score_time')
