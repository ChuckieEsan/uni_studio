import socket
import os
import logging
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
VERSION = os.popen('git rev-parse --short HEAD').read()
config = {}
DEBUG = False if ip == '172.31.240.127' else True  # 172.31.240.127 is dutbit.com
config['DEBUG'] = DEBUG
if DEBUG:
    import fakeredis
    sv = fakeredis.FakeServer()
    r = fakeredis.FakeStrictRedis(server=sv)
else:
    import redis
    r = redis.Redis(host='localhost',port=6379,decode_responses=False,password='Bit_redis_123', socket_timeout=0.5)

try:
    r.ping()
    if DEBUG:
        fake_interceptor = ['/console/issues','/vote']
        fake_id = 'abc123'
        fake_sessionid = 'sessionid456'
        sname = 'studio:global_interceptor'
        for f in fake_interceptor:
            r.sadd(sname,f)
        r.set(fake_sessionid,fake_id)
        r.hset('userservice:userinfo:'+fake_id,mapping={'username':'tester','email':'123@dutbit.com'})
        r.hset('userservice:rolemap:'+fake_id,mapping={'super_admin':'true','vol_time_admin':'true','vote_admin':'true','default_user':'true'})
except Exception as e:
    print(e)
    exit()

from flask import Flask, Request, session, render_template
from flask_session import Session
from flask_bootstrap import Bootstrap  # for flask-file-uploader | fileservice
from flask_migrate import Migrate
from .test import tests
from .fileservice.app import app as fileserviceapp
from .api import postcardapp
from .utils.dir_helper import join_upload_dir
from .utils.ver_helper import get_ver
from .utils.error_helper import error_handler
from .interceptors import global_interceptor
from .apps.console import console as consoleapp
from .apps.common import common as commonfileapp
from .apps.issues import issues as issuesapp
from .apps.vol_time import vol_time as vol_timeapp
from .staticfile.app import app as staticfileapp
from .apps.vote import vote as voteapp
subdomains = {
    'DEVELOPMENT':{
        'www':'',
        'files':'',
    },
    'PRODUCTION':{
        'www':'www',
        'files':'files',
    }
}

def create_app():
    app = Flask(__name__)

    #set up logger
    try:
        os.mkdir('log')
    except:
        pass
    handler = logging.FileHandler('log/service.log')
    logging_format = logging.Formatter('%(levelname)s - %(asctime)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    #set up global interceptor
    app.before_request(global_interceptor)

    with app.app_context():
        Bootstrap(app)

        from studio.models import db
        app.logger.info('hi')
        if ip == '172.31.240.127':  # is dutbit.com
            print('------ starting service in production ------')
            app.config['DEBUG'] = False
            app.config['SERVER_NAME'] = 'dutbit.com'
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
            app.config['SUBDOMAINS'] = subdomains['PRODUCTION']
            app.config['SESSION_TYPE'] = 'filesystem'
            if 'mysql+pymysql' not in app.config['SQLALCHEMY_DATABASE_URI']:
                raise EnvironmentError("No db connection uri provided")
                exit(-1)
        else:
            print('------ starting service in development ------')
            app.config['DEBUG'] = True
            app.config['SERVER_NAME'] = '127.0.0.1:5000'
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
            app.config['SUBDOMAINS'] = subdomains['DEVELOPMENT']
            app.config['SESSION_TYPE'] = 'filesystem'
        app.config['VERSION'] = VERSION
        app.config['CAPTCHA_LEN'] = 4
        app.config['CAPTCHA_TTL'] = 60
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_PERMANENT'] = True  #sessons是否长期有效，false，则关闭浏览器，session失效
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600   #session长期有效，则设定session生命周期，整数秒，默认大概不到3小时。
        app.add_template_global(get_ver)
        Session(app)
        db.init_app(app)
        migrate = Migrate(app,db)
        # db.drop_all()
        db.create_all()
        for i in (400,401,404,403,500,503):
            app.register_error_handler(i,error_handler)
        app.register_blueprint(tests)
        app.register_blueprint(fileserviceapp,url_prefix='/fileservice',subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(fileserviceapp,url_prefix='',subdomain=app.config['SUBDOMAINS']['files'])
        app.register_blueprint(staticfileapp,url_prefix='/staticfile',subdomain='www')
        app.register_blueprint(voteapp,url_prefix='/vote',subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(postcardapp)
        app.register_blueprint(issuesapp,url_prefix="/issues",subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(commonfileapp,url_prefix="/common",subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(consoleapp,url_prefix="/console",subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(vol_timeapp,url_prefix="/vol_time",subdomains=app.config['SUBDOMAINS']['www'])
        #app.config['SERVER_NAME'] = 'dutbit.com'
        app.config['SECRET_KEY'] = 'Do not go gentle into that good night'
        app.config['FILESERVICE_UPLOAD_FOLDER'] = join_upload_dir('data/')
        app.config['FILESERVICE_THUMBNAIL_FOLDER'] = join_upload_dir('data/thumbnail/')
        app.config['FILESERVICE_MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
        return app
