from flask import Flask, jsonify
from config import get_settings
import views

app = Flask(__name__)
settings = get_settings()

#URLs
app.add_url_rule('/', view_func=views.index)

API_VER_1 = '/api/v1/'
app.add_url_rule(API_VER_1 + 'profile/<person_id>',
        view_func=views.profile, methods=['GET', ])
app.add_url_rule(API_VER_1 + 'register',
        view_func=views.register, methods=['POST', ])
app.add_url_rule(API_VER_1 + 'login',
        view_func=views.login, methods=['POST', ])
app.add_url_rule(API_VER_1 + 'point',
        view_func=views.point, methods=['GET', 'POST'])


'''
Useful Server Errors
'''


@app.errorhandler(400)
def error400(err):
    msg = {'success': False,
            'msg': err.__str__(),
            'reason': 'Possibly did not give enough arguments'
            }
    return jsonify(msg)


@app.errorhandler(404)
def error404(err):
    msg = {'success': False,
            'msg': err.__str__(),
            'reason': 'Possibly malformed URL'
            }
    return jsonify(msg)


@app.errorhandler(405)
def error405(err):
    msg = {'success': False,
            'msg': err.__str__(),
            'reason': 'This method is not allowed'
            }
    return jsonify(msg)


@app.errorhandler(500)
def error500(err):
    msg = {'success': False,
            'msg': err.__str__(),
            'reason': 'Fish! You almost crashed the server'
            }
    return jsonify(msg)


if __name__ == '__main__':
    app.add_url_rule('/open_debugger',
            view_func=views.open_debugger)
    app.run(
        port=8888,
        debug=True,
        host='0.0.0.0'
        )
