from functools import wraps
from flask import request,redirect,current_app,abort,g,jsonify,url_for,flash,g,Request,Response
import json
import time
from studio.models import db,UserRoles,RouteInterceptors,UserUsers
from studio.cache import cache

CAPTCHA_TIMEOUT = 600
CAPTCHA_NAMESPACE = 'captcha'
CAPTCHA_COOKIE_KEY = '_c'
CAPTCHA_VALID_FIELD = 'is_valid'

def global_interceptor():
    token = request.cookies.get('token')
    try:
        data = current_app.tjwss.loads(token)
        user = UserUsers.query.filter(UserUsers.id==data.get('id')).first()
        g.user = user
        current_app.logger.info("user=",g.user)
    except Exception as e:
        g.user = None
    if request.path.startswith('/console') and not g.user:
        return redirect(url_for('users.users_entrypoint')+'?target={}'.format(request.path))
    rules = RouteInterceptors.query.filter(RouteInterceptors.delete==False).all()
    for r in rules:
        if not request.path.startswith(r.startswith):#这里很有可能有问题，应该尝试匹配最长路径。
            continue
        if not user:
            return redirect(url_for('users.users_entrypoint')+'?target={}'.format(request.path))
        if r.role_bits == 0 and not (user.role_bits & 1): # only root can view this page
            return abort(503)
        if not (user.role_bits & 1 or user.role_bits & r.role_bits):
            flash(r.description)
            return abort(403)
            
def generate_response(success:bool,details:str)->Response:
    print(details)
    acc = request.headers.get('accept') or request.headers.get('Accept')
    if 'text/html' in acc:
        flash(details)
        abort(401)
    elif 'application/json' in acc:
        return jsonify({"success":success,"details":details})
    else:
        return jsonify({"success":success,"details":details})

def validate_captcha(func):
    @wraps(func)
    def func_wrapper(*args,**kwargs):
        uuid = request.cookies.get(CAPTCHA_COOKIE_KEY)
        if not uuid:
            return generate_response(False,'验证码已过期')

        captcha_text = cache.get('{}:{}'.format(CAPTCHA_NAMESPACE,uuid))
        if not captcha_text:
            return generate_response(False,'验证码已失效')

        if 'captcha' not in request.values:
            return generate_response(False,'验证码缺失')
        
        if request.values.get('captcha') != captcha_text:
            return generate_response(False,'验证码错误')
    
        return func(*args,**kwargs)
    return func_wrapper

