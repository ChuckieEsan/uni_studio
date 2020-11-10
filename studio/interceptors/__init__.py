from studio.session import session_exists
from studio import r#redis_conn
from functools import wraps
from flask import request,redirect,current_app,abort,g
import json
import redis
""" USAGE:
@app.route('/<id>')
@session_required
@roles_required(['super_admin'])
def ho(id):
    return 'bruhalsdfa'+id

#this is intended to be read-only
"""
def session_required(func):
    @wraps(func)
    def func_wrapper(*args,**kwargs):
        if current_app.config['DEBUG']:
            g.sessionid = 'abcdefgh'*4
            g._id = '_id-test123'
            return func(*args,**kwargs)
        sessionid = request.cookies.get('SESSIONID')
        if sessionid is None or len(sessionid)!=32:
            return redirect("/userservice/index.html?authrequired")
        if r.exists(sessionid):
            g.sessionid = sessionid
            user_info = r.hmget(sessionid,'_id')
            g._id = user_info[0]
            return func(*args,**kwargs)
        else:
            return redirect("/userservice/index.html?authrequired")
    return func_wrapper


def roles_required(roles:list):
    def check_roles(func):
        @wraps(func)
        def func_wrapper(*args,**kwargs):
            try:
                sessionid = g.sessionid
            except:
                print('programming error: no session_required decorator previously used in this context.')
                return abort(500)
            if current_app.config['DEBUG']:
                g.role = ['super_admin']
                if request.values.get('role') is not None:
                    g.role = [request.values.get('role')]
                print('debug mode, ignoring requirements, role is now',g.role)
                return func(*args,**kwargs) 
            try:
                user_info = r.hmget(sessionid,'site')
                role_info = json.loads(user_info)[0]
                role_intersection = set(roles)&set(role_info.keys())
                if not role_intersection:
                    raise ValueError
                g.role = role_intersection
                g._id = user_info[1]
            except redis.DataError:#no sessionid
                #print('no sessionid')
                return redirect('/userservice/index.html#1')
            except TypeError:#hmget returned none, no valid userservice session.
                #print('no valid session')
                return redirect('/userservice/index.html#2')
            except ValueError:
                #print('no valid role')
                return abort(404)
            except Exception as e:
                print(e)
                return abort(500)
            return func(*args,**kwargs)
        return func_wrapper
    return check_roles
