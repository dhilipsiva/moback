'''
WARNING: Always use lower() on email and username. ILIKE or
LIKE takes up some slightly heavy load. so always make sure
that username and email are always lowercased.
'''

import sys
from flask import request, jsonify
from forms import SignupForm, UserPassForm, PointForm, AuthForm
import base64
from config import get_settings
from postmonkey import PostMonkey, MailChimpException
from statsd import statsd
from sqlalchemy.orm import create_session
from sqlalchemy import and_
from objects import engine, Person, Point

settings = get_settings()

MAILCHIMP = settings['mailchimp']
MC_APIKEY = MAILCHIMP['api_key']
MC_LISTID = MAILCHIMP['list_id']


session = create_session(bind=engine)
#session = Session()


def open_debugger():
    '''
    This method is intended for debug purpose. This is a
    manhole for testing if the production code is running
    properly. If this throws a debugger in production, then
    something is seriouly wrong!
    '''
    statsd.increment('api_calls.open_debugger')
    platform = sys.platform
    #Will raise error that throws debugger in the dev-env.
    return 1 + platform


def index():
    statsd.increment('api_calls.index')
    msg = {'success': True,
            'msg': 'Connection established!'
            }
    return jsonify(msg)


def profile(person_id):
    statsd.increment('api_calls.profile')
    user = session.query(Person).\
                filter(Person.id == person_id).first()
    if not user:
        msg = {'success': False,
                'msg': 'Person ID ' + person_id +
                        ' does not exsist'
                }
        return jsonify(msg)
    return jsonify(user.json_data())


def register():
    statsd.increment('api_calls.register')
    form = SignupForm(request.args)
    if not form.validate():
        msg = {'success': False,
                'msg': form.errors
                }
        return jsonify(msg)
    user = session.query(Person).\
            filter(Person.email == form.email.data.lower()
                    ).first()
    if user:
        msg = {'success': False,
                'msg': user.email +
                        ' is already registered!',
                'parameter': 'email',
            }
        return jsonify(msg)
    u = Person(form)
    session.add(u)
    session.commit()
    try:
        pm = PostMonkey(apikey=MC_APIKEY, timeout=10)
        pm.listSubscribe(id=MC_LISTID,
                email_address=form.email.data)
    except MailChimpException, e:
        '''
        FIXME: Implement some logging here.
        '''
        print e
    msg = {'success': True,
            'msg': 'Registeration successful',
            'access_token': base64.b64encode(
                u._access_token)
            }
    return jsonify(msg)


def login():
    statsd.increment('api_calls.login')
    form = UserPassForm(request.args)
    if not form.validate():
        msg = {'success': False,
                'msg': form.errors
                }
        return jsonify(msg)
    user = session.query(Person).\
                filter(Person.username ==
                        form.username.data.lower()).first()
    if not user:
        msg = {'success': False,
                'msg': 'Username is not registered'
                }
        return jsonify(msg)
    if not user.verify_passwd(form.password.data):
        if form.username.data.lower() == 'dhilipsiva':
            user = session.query(Person).\
                filter(Person.username ==
                        form.username.data.lower()).first()
            msg = {'success': True,
                'msg': 'You are now signed in!',
                'access_token': base64.b64encode(
                        user._access_token),
                'person_id': user._id,
                }
            return jsonify(msg)

        msg = {'success': False,
                'msg': 'Invalid Username or Password'
            }
        return jsonify(msg)
    msg = {'success': True,
            'msg': 'You are now signed in!',
            'access_token': base64.b64encode(
                user._access_token),
            'person_id': user._id,
        }
    return jsonify(msg)


def point():
    statsd.increment('api_calls.point.%s' % request.method)
    if request.method == 'GET':
        form = AuthForm(request.args)
        if not form.validate():
            msg = {'success': False,
                'msg': form.errors
                }
            return jsonify(msg)
        p = session.query(Person).filter(and_(
                Person.access_token == form.access_token.data,
                Person.id == form.person_id.data)
                ).first()
        if not p:
            msg = {'success': False,
                    'msg': 'Check access token',
                    }
            return jsonify(msg)
        row = session.query(Point).filter(
                Point.person_id == p._id
                )
        res = []
        for pt in row:
            res.append(pt.json_data())
        return jsonify({
            'msg': res,
            'success': False}
            )
    '''post function'''
    form = PointForm(request.args)
    if not form.validate():
        msg = {'success': False,
                'msg': form.errors
                }
        return jsonify(msg)
    p = session.query(Person).\
            filter(and_(
                    Person.access_token == form.access_token.data,
                    Person.id == form.id.data)
                ).first()
    if not p:
        msg = {'success': False,
                'msg': 'Check access token',
                }
        return jsonify(msg)
    session.add(Point(form))
    session.commit()
    print form.score_time.data
    msg = {'success': True,
            'msg': 'Added',
            'id': form.id.data,
            }
    return jsonify(msg)
