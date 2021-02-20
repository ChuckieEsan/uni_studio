
from functools import wraps
from flask import request,redirect,current_app,abort,g,session,jsonify,url_for,flash
from studio import r,DEBUG#redis_conn
if DEBUG:
    from studio import fake_id,fake_sessionid
import json
import redis
import time
from studio.utils.captcha_helper import getcaptcha
from studio.utils.rules_helper import get_rules
from studio.models import db,UserRoles,RouteInterceptors
def global_interceptor():
    rules = RouteInterceptors.query.filter(RouteInterceptors.delete==False).all()
    for r in rules:
        if request.path.startswith(r.startswith):
            rb = r.role_bits
            try:
                u_rb = int(session.get('role_bits'))
            except Exception as e:
                current_app.logger.error(e)
                return redirect(url_for('users.users_entrypoint')+'?target={}'.format(request.path))
            if rb == 0:
                if not u_rb & 1:#super_admin
                    abort(503)
            else:
                if not (u_rb & 1 or u_rb & rb):
                    flash(r.description)
                    return abort(403)
            

def set_captcha(func):
    @wraps(func)
    def func_wrapper(*args,**kwargs):
        session['captcha_text'] = getcaptcha(current_app.config['CAPTCHA_LEN'])
        session['captcha_time'] = int(time.time())

        return func(*args,**kwargs)
    return func_wrapper

def validate_captcha(func):
    @wraps(func)
    def func_wrapper(*args,**kwargs):
        if not request.values.get('captcha'):
            return jsonify({'success':False,'details':'验证码缺失'})
        if request.values.get('captcha') != session['captcha_text']:
            return jsonify({'success':False,'details':'验证码错误'})
        if int(time.time()) > (session['captcha_time']+current_app.config['CAPTCHA_TTL']):
            return jsonify({'success':False,'details':'验证码超时'})
        return func(*args,**kwargs)
    return func_wrapper

