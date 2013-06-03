from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, Table
import base64
from utils import hmac_sign
import uuid
from flask.ext.sqlalchemy import SQLAlchemy
from config import get_settings

'''
To create new secret-keys, use cookie_secret.py script
Warning : do not change after production. All validations
will fail if you do.
'''
secret_key = 'a_secret_key'

DBBase = declarative_base()


settings = get_settings()
dbSett = settings['db']
database = dbSett['database']
user = dbSett['username']
password = dbSett['password']
host = dbSett['host']
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://' + user +\
    ':' + password + '@' + host + '/' + database
db = SQLAlchemy(app)
metadata = MetaData(bind=db.engine)


class Person(DBBase):
    __table__ = Table('person', metadata, autoload=True)

    def __init__(self, form):
        try:
            self.id = int(form.id.data)
        except:
            self.id = None
        self.email = form.email.data
        self.firstname = form.firstname.data
        self.lastname = form.lastname.data
        self.username = form.username.data

        passwd = base64.b64decode(form.password.data)
        pw_hash = hmac_sign(secret_key, passwd)
        access_token = str(uuid.uuid5(
            uuid.uuid1(), str(uuid.uuid1())))

        self.pw_hash = pw_hash
        self.access_token = access_token

    @property
    def _id(self):
        return self.id

    @property
    def _access_token(self):
        return self.access_token

    def verify_passwd(self, passwd):
        passwd = base64.b64decode(passwd)
        pw_hash = hmac_sign(secret_key, passwd)
        return pw_hash == self.pw_hash

    def json_data(self):
        data = {
            'username': self.username,
            'total_score': self.total_score, }
        return data


class Score(DBBase):
    __table__ = Table('score', metadata, autoload=True)

    def __init__(self, form, person_id):
        self.id = form.id.data
        self.score_count = form.score_count.data
        self.score_time = form.score_time.data
        self.person_id = person_id

    def json_data(self):
        data = {
            'id': self.id,
            'person_id': self.person_id,
            'score_count': self.score_count,
            'score_time': str(self.score_time), }
        return data
