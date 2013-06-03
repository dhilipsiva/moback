import api


app = api.app


# URLs
## API URLs
app.add_url_rule('/', view_func=api.index)
app.add_url_rule(
    '/login',
    view_func=api.login, methods=['POST', ])
app.add_url_rule(
    '/register',
    view_func=api.register, methods=['POST', ])
app.add_url_rule(
    '/forgot_password',
    view_func=api.forgot_password, methods=['GET', 'POST', ])
app.add_url_rule(
    '/reset_page',
    view_func=api.reset_page, methods=['GET', 'POST', ])

API_VER_1 = '/api/v1/'
app.add_url_rule(
    API_VER_1 + 'profile/<person_id>',
    view_func=api.profile, methods=['GET', ])
app.add_url_rule(
    API_VER_1 + 'score',
    view_func=api.score, methods=['GET', 'POST', ])
app.add_url_rule(
    API_VER_1 + 'login_with_fb',
    view_func=api.login_with_fb, methods=['POST', ])
app.add_url_rule(
    API_VER_1 + 'leaderboard',
    view_func=api.leaderboard, methods=['GET', ])
app.add_url_rule(
    API_VER_1 + 'user_scores',
    view_func=api.user_scores, methods=['GET', ])

if __name__ == '__main__':
    app.run(
        port=8888,
        debug=True,
        host='0.0.0.0')
