'''
Make sure that username email and difficulty are
always lowercased.
'''

from wtforms.form import Form
from wtforms.validators import length, Email, required,\
    NumberRange
from wtforms.fields import TextField


class UserPassForm(Form):
    username = TextField(
        u'username',
        validators=[required(), ])
    password = TextField(
        u'password',
        validators=[required(), length(min=4, max=30)])

    def __init__(self, *args, **kwargs):
        super(UserPassForm, self).__init__(*args, **kwargs)
        if self.username.data:
            self.username.data = self.username.data.lower()


class EmailForm(Form):
    email = TextField(
        u'email',
        validators=[required(), Email(), ])

    sig = TextField(
        u'sig', validators=[required(), ])

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        if self.email.data:
            self.email.data = self.email.data.lower()


class SignupForm(UserPassForm, EmailForm):
    firstname = TextField(
        u'firstname',
        validators=[required(), ])
    lastname = TextField(
        u'lastname',
        validators=[required(), ])


class LoginFBForm(SignupForm):
    sig = TextField(
        u'sig',
        validators=[required(), ])


class ScoreForm(Form):
    id = TextField(
        u'id',
        validators=[required(), length(min=36, max=36)])
    score_count = TextField(
        u'score_count',
        validators=[required(), NumberRange(min=0)])
    score_time = TextField(u'score_time')

    def __init__(self, *args, **kwargs):
        super(ScoreForm, self).__init__(*args, **kwargs)
        if self.difficulty.data:
            self.difficulty.data = \
                self.difficulty.data.lower()
