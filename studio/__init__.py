import socket
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
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
except Exception as e:
    print(e)
    exit()

import os
from flask import Flask, Request, session
from flask_session import Session
from flask_bootstrap import Bootstrap  # for flask-file-uploader | fileservice
from .test import tests
from .fileservice.app import app as fileserviceapp
from .vote import vote as voteapp
from .api import postcardapp
from .common import common as commonfileapp
from .issues import issues as issuesapp
from .staticfile.app import app as staticfileapp
from .utils.dir_helper import join_upload_dir

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
    with app.app_context():
        Bootstrap(app)

        from studio.models import db

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
            print("Redis connection using",r.__class__.__name__)
            app.config['DEBUG'] = True
            app.config['SERVER_NAME'] = '127.0.0.1:5000'
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
            app.config['SUBDOMAINS'] = subdomains['DEVELOPMENT']
            app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_PERMANENT'] = True  #sessons是否长期有效，false，则关闭浏览器，session失效
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600   #session长期有效，则设定session生命周期，整数秒，默认大概不到3小时。
        Session(app)
        db.init_app(app)
        # db.drop_all()
        db.create_all()
        app.register_blueprint(tests)
        app.register_blueprint(fileserviceapp,url_prefix='/fileservice',subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(fileserviceapp,url_prefix='',subdomain=app.config['SUBDOMAINS']['files'])
        app.register_blueprint(staticfileapp,url_prefix='/staticfile',subdomain='www')
        app.register_blueprint(voteapp,url_prefix='/vote',subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(postcardapp)
        app.register_blueprint(issuesapp,url_prefix="/issues",subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(commonfileapp,url_prefix="/common",subdomain=app.config['SUBDOMAINS']['www'])
        #app.config['SERVER_NAME'] = 'dutbit.com'
        app.config['SECRET_KEY'] = 'Do not go gentle into that good night'
        app.config['FILESERVICE_UPLOAD_FOLDER'] = join_upload_dir('data/')
        app.config['FILESERVICE_THUMBNAIL_FOLDER'] = join_upload_dir('data/thumbnail/')
        app.config['FILESERVICE_MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
        return app
