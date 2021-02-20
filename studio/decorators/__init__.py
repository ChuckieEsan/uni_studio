from functools import wraps
import redis
import pickle
from flask import current_app
from studio.utils.hash_helper import md5
from threading import Lock
from studio import r#redis_conn
if r is None:
    try:
        r = redis.Redis(host='localhost',port=6379,decode_responses=False)
    except Exception as e:
        print(e)
        pass
def memoize(timeout:int=30):
    def _c(func):
        @wraps(func)
        def func_wrapper(*args,**kwargs):
            if r is None:
                return func(*args,**kwargs)
            if len(args)!=1:
                print('not for us')
                return func(*args,**kwargs)
            fname = func.__name__
            keyname = 'memoize:'+fname
            _m = r.get(keyname)
            if not _m:
                print('setting cache for',keyname,'setting timeout=',timeout)
                result = func(*args,**kwargs)
                r.set(keyname,pickle.dumps(result),ex=timeout)
                return result
            else:
                print('cache hit for',keyname)
                return pickle.loads(_m)
        return func_wrapper
    return _c

@memoize(10)
def add(a,b):
    print('cache not hit')
    return a+b

#print(add(2,3))

@memoize(20)
def times(a):
    return a*10
mutex = Lock()
def memo(timeout:int=6000):
    
    def _c(func):
        @wraps(func)
        def func_wrapper(*args,**kwargs):
            if r is None:
                print('redis is none')
                return func(*args,**kwargs)
            
            fname = func.__name__
            keyname = 'memo:'+fname
            with mutex:
                _m = r.get(keyname)
                if not _m:
                    print('setting cache for',keyname,'setting timeout=',timeout)
                    result = func(*args,**kwargs)
                    r.set(keyname,pickle.dumps(result),ex=timeout)
                    return result
                else:
                    print('cache hit for',keyname)
                    return pickle.loads(_m)
        return func_wrapper
    return _c

if __name__ == "__main__":
    print(times(5))
    print(times(10))
    print(times(20))
    print(times(5))