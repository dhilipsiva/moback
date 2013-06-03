from flask import request, jsonify, g, redirect, \
    url_for, abort, render_template, session as flask_session
from forms import SignupForm, UserPassForm, ScoreForm, \
    LoginFBForm, EmailForm
import base64
from postmonkey import PostMonkey, MailChimpException
from statsd import statsd
from sqlalchemy import and_, desc, func
from objects import db, Person, Score, \
    secret_key, settings, app, InAppProducts
from functools import wraps
from sqlalchemy.sql.expression import alias
import datetime
from flask_mail import Mail, Message
import urllib
from uuid import uuid1, uuid5
from utils import hmac_sign

logger = app.logger

MAILCHIMP = settings['mailchimp']
MC_APIKEY = MAILCHIMP['api_key']
MC_LISTID = MAILCHIMP['list_id']

for key in settings['mail-config'].keys():
    app.config[key.upper()] = settings['mail-config'][key]

session = db.session
mail = Mail(app)

app.secret_key = secret_key

'''
Useful Server Errors
'''


@app.errorhandler(400)
def error400(err):
    logger.error("400: " + err.__str__())
    msg = {
        'success': False,
        'msg': '400: Error',
        'reason': 'Possibly did not give enough arguments'}
    return jsonify(msg)


@app.errorhandler(401)
def error401(err):
    logger.error("401: " + err.__str__())
    msg = {
        'success': False,
        'msg': '401: Error',
        'reason': 'Authorization Headers not found', }
    return jsonify(msg)


@app.errorhandler(403)
def error403(err):
    logger.error("403: " + err.__str__())
    msg = {
        'success': False,
        'msg': '403: Error',
        'reason': 'Forbidden'}
    return jsonify(msg)


@app.errorhandler(404)
def error404(err):
    logger.error("404: " + err.__str__())
    msg = {
        'success': False,
        'msg': '404: Error',
        'reason': 'Possibly malformed URL'}
    return jsonify(msg)


@app.errorhandler(405)
def error405(err):
    logger.error("405: " + err.__str__())
    msg = {
        'success': False,
        'msg': '405: Error',
        'reason': 'This method is not allowed'}
    return jsonify(msg)


@app.errorhandler(500)
def error500(err):
    logger.error("500: " + err.__str__())
    msg = {
        'success': False,
        'msg': '500: Error',
        'reason': 'Fish! You almost crashed the server'}
    return jsonify(msg)


@app.errorhandler(501)
def error501(err):
    logger.error("501: " + err.__str__())
    msg = {
        'success': False,
        'msg': '501: Error',
        'reason': 'Fish! You almost crashed the server'}
    return jsonify(msg)


def authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        person_id, token = base64.decodestring(
            request.headers[
                'Authorization'].strip(
                    'Token token=').replace('"', '')).\
            split(':')
        if token == '':
            return abort(401)
        user = session.query(Person).filter(and_(
            Person.id == person_id,
            Person.access_token == token)).first()
        if user:
            g.user = user
            return f()
        else:
            return abort(401)
    return decorated_function


def generate_csrf_token():
    if '_csrf_token' not in flask_session:
        flask_session['_csrf_token'] = str(uuid5(
            uuid1(), str(uuid1())))
    return flask_session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token


def index():
    statsd.increment('api_calls.index')
    msg = {
        'success': True,
        'msg': 'Connection established!'}
    return jsonify(msg)


@authenticated
def profile():
    statsd.increment('api_calls.profile')
    return jsonify(g.user.json_data())


def _user_return(user):
        msg = {
            'success': True,
            'msg': 'You are now signed in!',
            'access_token': base64.b64encode(
                user._access_token),
            'person_id': user._id, }
        logger.info(msg)
        return jsonify(msg)


def register():
    statsd.increment('api_calls.register')
    form = SignupForm(request.form)
    logger.info(request.form)
    if not form.validate():
        msg = {
            'success': False,
            'msg': form.errors}
        return jsonify(msg)
    user = session.query(Person).\
        filter(Person.email == form.email.data
               ).first()
    if user:
        msg = {
            'success': False,
            'msg': user.email + ' is already registered!',
            'parameter': 'email', }
        return jsonify(msg)
    u = Person(form)
    session.add(u)
    session.commit()
    try:
        pm = PostMonkey(apikey=MC_APIKEY, timeout=10)
        pm.listSubscribe(
            id=MC_LISTID, email_address=form.email.data)
    except MailChimpException, e:
        app.logger.error(str(e))
    return _user_return(u)


def login():
    logger.info(request.form)
    statsd.increment('api_calls.login')
    form = UserPassForm(request.form)
    if not form.validate():
        msg = {
            'success': False,
            'msg': form.errors}
        return jsonify(msg)
    user = session.query(Person).\
        filter(
            Person.username == form.username.data).first()
    if not user:
        msg = {
            'success': False,
            'msg': 'Username is not registered'}
        return jsonify(msg)
    if not user.verify_passwd(form.password.data):
        msg = {
            'success': False,
            'msg': 'Invalid Username or Password'}
        return jsonify(msg)
    return _user_return(user)


@authenticated
def score():
    statsd.increment('api_calls.score.%s' % request.method)
    if request.method == 'GET':
        row = session.query(Score).filter(
            Score.person_id == g.user._id)
        res = []
        for pt in row:
            res.append(pt.json_data())
        return jsonify({
            'msg': res,
            'success': False})

    '''post function'''
    logger.info(request.form)
    form = ScoreForm(request.form)
    if not form.validate():
        msg = {
            'success': False,
            'msg': form.errors}
        return jsonify(msg)
    session.add(Score(form, g.user._id))
    session.commit()
    msg = {
        'success': True,
        'msg': 'Added',
        'id': form.id.data, }
    return jsonify(msg)


def inapp_products():
    statsd.increment('api_calls.inapp_products')
    prods = session.query(InAppProducts)
    prod_array = []
    for prod in prods:
        prod_array.append(prod.json_data())
    msg = {
        'success': True,
        'msg': prod_array, }
    return jsonify(msg)


def login_with_fb():
    statsd.increment('api_calls.login_with_fb')
    form = LoginFBForm(request.form)
    logger.info(request.form)
    if not form.validate():
        msg = {
            'success': False,
            'msg': form.errors}
        return jsonify(msg)
    if secret_key != base64.b64decode(form.sig.data):
        msg = {
            'success': False,
            'msg': 'invalid signature'}
        return jsonify(msg)
    user = session.query(Person).\
        filter(Person.email == form.email.data).first()
    if user:
        return _user_return(user)
    user = Person(form)
    session.add(user)
    session.commit()
    return _user_return(user)


def _alltime_leaderboard():
    top_scorers = session.query(Person).\
        order_by(desc(Person.total_score)).limit(10)
    score_array = []
    for score in top_scorers:
        score_array.append(score.json_data())
    return score_array


def _get_tops(days):
    time_limit = datetime.datetime.now() \
        - datetime.timedelta(days=days)
    total_alias = alias(func.sum(Score.score_count))
    top_scorers = session.query(
        Person.username, func.sum(Score.score_count)).\
        filter(and_(Person.id == Score.person_id,
               Score.score_time > time_limit)).\
        group_by(Person.username).\
        order_by(desc(total_alias)).\
        limit(10).all()
    tops = []
    for top in top_scorers:
        top_dict = {
            'username': top[0],
            'total_score': top[1]}
        tops.append(top_dict)
    return tops


def leaderboard():
    statsd.increment('api_calls.leaderboard')
    msg = {
        'success': True,
        'msg': 'leaderboards',
        'all_time': _alltime_leaderboard(),
        'month': _get_tops(30),
        'week': _get_tops(7),
        'day': _get_tops(1), }
    return jsonify(msg)


@authenticated
def user_scores():
    statsd.increment('api_calls.user_scores')
    scrs = session.query(Score).\
        filter(Score.person_id == g.user.id)
    scr_ary = []
    for scr in scrs:
        scr_ary.append(scr.json_data())
    msg = {
        'success': True,
        'msg': 'user\'s scores',
        'scores': scr_ary}
    return jsonify(msg)


def forgot_password():
    statsd.increment('api_calls.forgot_password')
    if request.method == 'POST':
        logger.info(request.form)
        form = EmailForm(request.form)
        if not form.validate():
            msg = {
                'success': False,
                'msg': form.errors, }
            return jsonify(msg)
        if secret_key != base64.b64decode(form.sig.data):
            msg = {
                'success': False,
                'msg': 'invalid signature'}
            return jsonify(msg)
        u = session.query(Person).\
            filter(Person.email == form.email.data).\
            first()
        if not u:
            msg = {
                'success': False,
                'msg': 'Email not registered!'}
            return jsonify(msg)
        m = Message(
            "Reset Password",
            recipients=[form.email.data])
        content = (
            'Click <a href="http://' +
            request.headers['Host'] + '/forgot_password?' +
            'key=' + urllib.quote(u.pw_hash) + '&email=' +
            urllib.quote(form.email.data) + '">HERE</a>' +
            ' to reset your password')
        m.html = content
        mail.send(m)
        msg = {
            'success': True,
            'msg': 'Mail Sent!'}
        return jsonify(msg)

    logger.info(request.args)
    key = urllib.unquote(request.args['key'])
    email = urllib.unquote(request.args['email'])
    u = session.query(Person).\
        filter(Person.email == email).first()
    if u and key == u.pw_hash:
        response = redirect(url_for('reset_page'))
        response.set_cookie('email', value=email)
        response.set_cookie('key', value=urllib.quote(key))
        return response
    return 'Invalid key!'


def reset_page():
    statsd.increment('api_calls.reset_page')
    logger.info(request.form)
    if request.method == 'GET':
        return render_template('reset_page.html')
    token = flask_session.pop('_csrf_token', None)
    if not token or token != request.form.get('_csrf_token'):
        return render_template(
            'reset_page.html',
            error='Did you really think that this will work?')
    pwd1 = request.form.get('pwd1', None)
    pwd2 = request.form.get('pwd2', None)
    if pwd1 != pwd2:
        return render_template(
            'reset_page.html',
            error='Passwords does not match!')
    if not pwd1 or len(pwd1) < 6:
        return render_template(
            'reset_page.html',
            error='Password must be atleast 6 chars!')
    email = request.cookies.get('email')
    u = session.query(Person).\
        filter(Person.email == email).first()
    key = urllib.unquote(request.cookies.get('key', None))
    if key != u.pw_hash:
        return render_template(
            'reset_page.html',
            error='Key invalid or expired!')
    pw_hash = hmac_sign(secret_key, pwd1)
    access_token = str(uuid5(uuid1(), str(uuid1())))
    session.query(Person).filter(Person.email == email).\
        update({
            'pw_hash': pw_hash,
            'access_token': access_token, })
    session.commit()
    return render_template(
        'reset_page.html',
        error='Password Changed successfully')
