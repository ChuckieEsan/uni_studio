from itsdangerous import NoneAlgorithm
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, Response, jsonify, g, request, current_app, abort
from flask_cors import CORS
from studio.models.user import db, UserUsers
from studio.models.route import RouteInterceptors
from studio.utils.cache import cache
from .dayImage import dayImage
from .issue import issue
from .point import point
from .pointMan import point_man
from .user import user
from .voltime import voltime
from .voltimeMan import voltime_man
from typing import List

apivue = Blueprint("apivue", __name__, url_prefix='/apivue')
apivue.register_blueprint(dayImage)
apivue.register_blueprint(issue)
apivue.register_blueprint(point)
apivue.register_blueprint(point_man)
apivue.register_blueprint(user)
apivue.register_blueprint(voltime)
apivue.register_blueprint(voltime_man)
CORS(apivue)


@cache.memoize(30)
def get_all_rules() -> List[RouteInterceptors]:
    print('RouteInterceptors')
    return RouteInterceptors.query.order_by(RouteInterceptors.startswith.desc()).all()


@cache.memoize(3)
def get_user(_id):
    return UserUsers.query.filter(UserUsers.id == _id).first()


@apivue.before_request
def interceptor():
    try:
        token = request.headers.get("Authorization")
        dictToken = current_app.tjwss.loads(token)
        user = get_user(dictToken['id'])
        g.user = user
        current_app.logger.info("user=", g.user.id)
    except Exception as e:
        g.user = None
    # r.role_bits: 1 root用户, 2 默认用户
    rules = get_all_rules()
    for r in rules:
        if not request.path.startswith(r.startswith):
            continue

        if g.user is None:
            return jsonify({"success": False, "details": "需要登录", 'login_target': request.path})
        elif not g.user.validated:
            # if not g.user.validation_code:
            #     code = getcaptcha(4)
            #     UserUsers.query.filter(UserUsers.id == g.user.id).update({'validation_code': code})
            #     send_validation_code(to=g.user.email, code=code)
            #     db.session.commit()
            if current_app.config['DEBUG']:
                print(g.user.validation_code)
            return jsonify({"success": False, "details": "需要验证", 'login_target': request.path})
        elif not (user.role_bits & 1 or user.role_bits & r.role_bits):
            # 不是【root用户 或者 有该权限的用户】
            # flash(r.description)
            return abort(403)
        else:
            break


@apivue.route('/login', methods=['POST'])
def users_login():
    dicForm: dict = request.get_json()
    user = UserUsers.query.filter(UserUsers.email == str(dicForm.get('email'))).one_or_none()

    if user is None:
        return jsonify({"success": False, "details": "Incorrect."})
    elif not user.check_password(dicForm.get('password')):
        return jsonify({"success": False, "details": "Incorrect password."})
    else:
        dictToken = {'id': user.id}
        token = current_app.tjwss.dumps(dictToken).decode()
        return jsonify({"success": True, 'token': token})


@apivue.route('/register', methods=['POST'])
def register():
    dicForm: dict = request.get_json()

    if dicForm.get('email') is None:
        return jsonify({"success": False, "details": "email is required."})
    elif dicForm.get('password') is None:
        return jsonify({"success": False, "details": "Password is required."})
    else:
        try:
            user = UserUsers(kwargs=dicForm)
            db.session.add(user)
            db.session.commit()
        # except db.IntegrityError:
        #     error = f"User {username} is already registered."
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"success": False, "details": "Exception"})
        else:
            return jsonify({"success": True})


# @apivue.route('/logout')
# def users_logout():
#     response = make_response(redirect(url_for('users.users_entrypoint')))
#     response.set_cookie('token', '', max_age=1, domain=current_app.config['SERVER_NAME'], secure=True, httponly=True)
#     return response