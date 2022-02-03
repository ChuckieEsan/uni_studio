from flask import Blueprint, Response, jsonify, g, request, current_app
from flask_cors import CORS
from studio.models import db, UserUsers
from .dayImage import dayImage
from .issue import issue
from .voltime import voltime

MUST_LOGIN_PATH = ['/console', '/chat']

apivue = Blueprint("apivue", __name__, url_prefix='/apivue')
apivue.register_blueprint(dayImage)
apivue.register_blueprint(issue)
apivue.register_blueprint(voltime)
CORS(apivue)


@apivue.before_request
def interceptor():
    try:
        token = request.cookies['token']
        data = current_app.tjwss.loads(token)
        user = UserUsers.query.filter(UserUsers.id == data['id']).first()
        g.user = user
        current_app.logger.info("user=", g.user.id)
    except Exception as e:
        g.user = None

    for p in MUST_LOGIN_PATH:
        if request.path.startswith('/apivue' + p) and not g.user:
            return jsonify({"success": False, "details": "需要登录"})


@apivue.route('/login', methods=['POST'])
def users_login():
    data = request.get_json()
    user = UserUsers.query.filter(UserUsers.email == str(data.get('email')).strip())\
        .filter(UserUsers.password == str(data.get('password')).strip()).first()
    if user:
        info = {'id': user.id}
        token = current_app.tjwss.dumps(info).decode()
        resp: Response = jsonify({"success": True, 'token': token})
        return resp
    return jsonify({"success": False, "details": "用户名或密码错误"})
