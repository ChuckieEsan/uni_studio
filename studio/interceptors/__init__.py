from functools import wraps
from flask import request,redirect,current_app,abort,g,session,jsonify,url_for,flash,g
import json
import time
from studio.models import db,UserRoles,RouteInterceptors,UserUsers
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

