from functools import wraps
from typing import List
from flask import request, redirect, current_app, abort, g, jsonify, url_for, flash, g, Response
from studio.models import RouteInterceptors, UserUsers, db
from studio.cache import cache
from studio.utils.captcha_helper import getcaptcha
from studio.utils.send_mail import send_validation_code
CAPTCHA_TIMEOUT = 600
CAPTCHA_NAMESPACE = 'captcha'
CAPTCHA_COOKIE_KEY = '_c'
CAPTCHA_VALID_FIELD = 'is_valid'
MUST_LOGIN_PATH = ['/console']


@cache.memoize(30)
def get_all_rules() -> List[RouteInterceptors]:
    return RouteInterceptors.query.filter(RouteInterceptors.delete == False).order_by(RouteInterceptors.startswith.desc()).all()


@cache.memoize(3)
def get_user(_id):
    return UserUsers.query.filter(UserUsers.id == _id).first()


def global_interceptor():
    # print(request.headers.get('X-Forwarded-For'))
    #request.remote_addr = request.headers.get('X-Forwarded-For')
    try:
        token = request.cookies['token']
        data = current_app.tjwss.loads(token)
        user = get_user(data['id'])
        g.user = user
        current_app.logger.info("user=", g.user.id)
    except Exception as e:
        g.user = None
        
    rules_hit = False
    for p in MUST_LOGIN_PATH:
        if request.path.startswith(p): 
            if not g.user:
                return redirect(url_for('users.users_entrypoint')+'?target={}'.format(request.path))
            else:
                rules_hit = True
    rules = get_all_rules()
    for r in rules:
        if not request.path.startswith(r.startswith):
            continue
        # only root can view this page
        if r.role_bits == 0 and not (g.user and g.user.role_bits & 1):
            flash(r.description)
            return abort(503)
        if not g.user:
            return redirect(url_for('users.users_entrypoint')+'?target={}'.format(request.path))
        if not (user.role_bits & 1 or user.role_bits & r.role_bits):
            flash(r.description)
            return abort(403)
        else:
            rules_hit = True
            break

    if rules_hit and not g.user.confirmed:
        if not g.user.validation_code:
            code = getcaptcha(4)
            UserUsers.query.filter(UserUsers.id == g.user.id).update(
                {'validation_code': code})
            send_validation_code(to=g.user.email,code=code)
            db.session.commit()
        if current_app.config['DEBUG']:
            print(g.user.validation_code)
        return redirect(url_for('users.users_confirm_index'))


def generate_response(success: bool, details: str) -> Response:
    print(details)
    acc = request.headers.get('accept') or request.headers.get('Accept')
    if 'text/html' in acc:
        flash(details)
        abort(401)
    elif 'application/json' in acc:
        return jsonify({"success": success, "details": details})
    else:
        return jsonify({"success": success, "details": details})


def validate_captcha(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        uuid = request.cookies.get(CAPTCHA_COOKIE_KEY)
        if not uuid:
            return generate_response(False, '验证码已过期')

        captcha_text = cache.get('{}:{}'.format(CAPTCHA_NAMESPACE, uuid))
        if not captcha_text:
            return generate_response(False, '验证码已失效')

        if 'captcha' not in request.values:
            return generate_response(False, '验证码缺失')

        if request.values.get('captcha') != captcha_text:
            return generate_response(False, '验证码错误')
        cache.delete('{}:{}'.format(CAPTCHA_NAMESPACE, uuid))
        return func(*args, **kwargs)
    return func_wrapper
