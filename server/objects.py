from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, create_engine, Table
import base64
import miscs
import uuid
from config import get_settings


'''
To create new secret-keys, use cookie_secret.py script
Warning : do not change after production. All validations
will fail if you do.
'''
secret_key = 'Oh6a4uJLS7WX8h64Pe/X0ubFoiypaUKktX0xNHXy1No='
DBBase = declarative_base()
settings = get_settings()
dbSett = settings['db']
database = dbSett['database']
user = dbSett['username']
password = dbSett['password']
host = dbSett['host']
engine = create_engine('postgresql+psycopg2://' + user +
        ':' + password + '@' + host + '/' + database,
        echo=True)
metadata = MetaData(bind=engine)


class Person(DBBase):
    __table__ = Table('person', metadata, autoload=True)

    def __init__(self, form):
        try:
            self.id = int(form.id.data)
        except:
            self.id = None
        self.email = form.email.data.lower()
        self.firstname = form.firstname.data
        self.lastname = form.lastname.data
        self.username = form.username.data.lower()

        passwd = base64.b64decode(form.password.data)
        pw_hash = miscs.hmac_sign(secret_key, passwd)
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
        pw_hash = miscs.hmac_sign(secret_key, passwd)
        return pw_hash == self.pw_hash

    def json_data(self):
        data = {'id': self.id,
                'email': self.email,
                'firstname': self.firstname,
                'lastname': self.lastname,
                'username': self.username,
                'start_date': str(self.start_date),
                'total_score': self.total_score,
        }
        return data


class Point(DBBase):
    __table__ = Table('point', metadata, autoload=True)

    def __init__(self, form):
        self.id = form.id.data
        self.person_id = form.person_id.data
        self.score = form.score.data
        self.score_time = form.score_time.data

    def json_data(self):
        data = {
                'id': self.id,
                'person_id': self.person_id,
                'score': self.score,
                'score_time': str(self.score_time),
                }
        return data
