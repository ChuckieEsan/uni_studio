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

# for flexibility, DO NOT do direct redis operations out of this interceptor module!!!
"""
def session_required(target:str=None):
    def _check_session(func):
        @wraps(func)
        def func_wrapper(*args,**kwargs):
            redirect_target = '/userservice/index.html' if target is None else "/userservice/index.html?target={}".format(target)
            if current_app.config['DEBUG']:
                g.sessionid = 'abcdefgh'*4
                g._id = '_id-test123'
                return func(*args,**kwargs)
            sessionid = request.cookies.get('SESSIONID')
            if sessionid is None or len(sessionid)!=32:
                return redirect(redirect_target)
            _id = r.get(sessionid)
            if _id is not None:
                g.sessionid = sessionid
                g._id = _id.decode('UTF-8')
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
            if current_app.config['DEBUG']:
                g.role = ['super_admin']
                if request.values.get('role') is not None:
                    g.role = [request.values.get('role')]
                print('debug mode, ignoring requirements, role is now',g.role)
                return func(*args,**kwargs) 
            try:
                role_info = r.hgetall("userservice:rolemap:"+g._id)
                role_keys = [j.decode('UTF-8') for j in role_info.keys()]
                role_intersection = set(roles)&set(role_keys)
                if not role_intersection:
                    raise ValueError
                g.role = role_intersection
            except redis.DataError:#no sessionid
                #print('no sessionid')
                return redirect('/userservice/index.html?target={}#1'.format(_redirect))
            except TypeError:#hmget returned none, no valid userservice session.
                #print('no valid session')
                return redirect('/userservice/index.html?target={}#2'.format(_redirect))
            except ValueError:
                #print('no valid role')
                #return abort(404)
                return redirect('/userservice/index.html?target={}#2'.format(_redirect))
            except Exception as e:
                print(e)
                return abort(500)
            return func(*args,**kwargs)
        return func_wrapper
    return check_roles
