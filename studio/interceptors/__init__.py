
from functools import wraps
from flask import request,redirect,current_app,abort,g,session,jsonify
from studio import r,DEBUG#redis_conn
if DEBUG:
    from studio import fake_id,fake_sessionid
import json
import redis
import time
from studio.utils.captcha_helper import getcaptcha
from studio.utils.rules_helper import get_rules
""" USAGE:
@app.route('/<id>')
@session_required
@roles_required(['super_admin'])
def ho(id):
    return 'bruhalsdfa'+id

#this is intended to be read-only

# for flexibility, DO NOT operate directly on redis outside of this interceptor module!!!
"""
def global_interceptor():
    sessionid = request.cookies.get('SESSIONID') if not current_app.config['DEBUG'] else fake_sessionid
    if sessionid != None:
        return
    rules = get_rules()
    for r in rules:
        if request.path.startswith(r):
            abort(503)
    pass


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

def session_required(target:str=None):
    def _check_session(func):
        @wraps(func)
        def func_wrapper(*args,**kwargs):
            redirect_target = '/userservice/index.html' if target is None else "/userservice/index.html?target={}".format(target)

            sessionid = request.cookies.get('SESSIONID') if not current_app.config['DEBUG'] else fake_sessionid
            if not current_app.config['DEBUG'] and (sessionid is None or len(sessionid)!=32):
                return redirect(redirect_target)
            _id = r.get(sessionid)
            if _id is not None:
                g.sessionid = sessionid
                g._id = _id.decode('UTF-8') if not current_app.config['DEBUG'] else fake_id
                return func(*args,**kwargs)
            else:
                return redirect(redirect_target)
        return func_wrapper
    return _check_session


def roles_required(roles:list,_redirect=None):
    def check_roles(func):
        @wraps(func)
        def func_wrapper(*args,**kwargs):
            try:
                sessionid = g.sessionid
            except:
                print('programming error: no session_required decorator previously used in this context.')
                return abort(500)
            try:
                role_info = r.hgetall("userservice:rolemap:"+g._id)
                role_keys = [j.decode('UTF-8') for j in role_info.keys()]
                if '*' in roles:
                    g.role = role_keys
                    return func(*args,**kwargs)
                role_intersection = set(roles)&set(role_keys)
                if not role_intersection:
                    raise ValueError
                g.role = role_intersection
            except redis.DataError:#no sessionid
                return redirect('/userservice/index.html?target={}#1'.format(_redirect))
            except TypeError:#hmget returned none, no valid userservice session.
                return redirect('/userservice/index.html?target={}#2'.format(_redirect))
            except ValueError:#no valid role
                return abort(401)
                #return redirect('/userservice/index.html?target={}#2'.format(_redirect))
            except Exception as e:
                print(e)
                return abort(500)
            return func(*args,**kwargs)
        return func_wrapper
    return check_roles
