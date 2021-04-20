import socket
import os
import logging
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
VERSION = os.popen('git rev-parse --short HEAD').read()
DEBUG = False if ip == '172.31.240.127' else True  # 172.31.240.127 is dutbit.com


from itsdangerous import TimedJSONWebSignatureSerializer as TJWSS
from flask import Flask, Request, render_template
from flask_bootstrap import Bootstrap  # for flask-file-uploader | fileservice
from flask_migrate import Migrate
from .cache import cache
from .test import tests
from .apps.fileservice.app import app as fileserviceapp
from .api import postcardapp
from .utils.dir_helper import join_upload_dir
from .utils.ver_helper import get_ver
from .utils.error_helper import error_handler
from .utils.log import LiveLog
from .interceptors import global_interceptor
from .apps.console import console as consoleapp
from .apps.common import common as commonfileapp
from .apps.issues import issues as issuesapp
from .apps.vol_time import vol_time as vol_timeapp
from .apps.staticfile.app import app as staticfileapp
from .apps.vote import vote as voteapp
from .apps.users import users as usersapp
from .apps.enroll import enroll as enrollapp
from .apps.h5 import h5 as h5app

def create_app():
    app = Flask(__name__)

    #set up logger
    try:
        os.mkdir('log')
    except:
        pass
    handler = logging.FileHandler('log/service.log')
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter('%(levelname)s - %(asctime)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)
    #set up global interceptor
    app.before_request(global_interceptor)
    for i in (400,401,404,403,500,503):
        app.register_error_handler(i,error_handler)
    with app.app_context():
        from studio.models import db
        print('---- debug = {} ----'.format(DEBUG))
        app.config['LIVE_LOG'] = LiveLog()
        app.config['VERSION'] = VERSION
        app.config['CAPTCHA_LEN'] = 4
        app.config['CAPTCHA_TTL'] = 60
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db' if DEBUG else os.environ['SQLALCHEMY_DATABASE_URI']
        if (not DEBUG) and 'mysql+pymysql' not in app.config['SQLALCHEMY_DATABASE_URI']:
            raise EnvironmentError("No db connection uri provided")
            exit(-1)
        app.config['SERVER_NAME'] = '127.0.0.1:5000' if DEBUG else 'www.dutbit.com'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.add_template_global(get_ver)
        db.init_app(app)
        cache.init_app(app)
        Bootstrap(app)
        # db.drop_all()
        db.create_all()
        migrate = Migrate(app,db)
        app.register_blueprint(tests)
        app.register_blueprint(fileserviceapp,url_prefix='/fileservice')
        app.register_blueprint(staticfileapp,url_prefix='/staticfile')
        app.register_blueprint(voteapp,url_prefix='/vote')
        app.register_blueprint(postcardapp,url_prefix='/postcard')
        app.register_blueprint(issuesapp,url_prefix="/issues")
        app.register_blueprint(commonfileapp,url_prefix="/common")
        app.register_blueprint(consoleapp,url_prefix="/console")
        app.register_blueprint(vol_timeapp,url_prefix="/vol_time")
        app.register_blueprint(usersapp,url_prefix="/user")
        app.register_blueprint(enrollapp,url_prefix = "/enroll")
        app.register_blueprint(h5app,url_prefix = "/h5")
        #app.config['SERVER_NAME'] = 'dutbit.com'
        app.config['TOKEN_EXPIRES_IN'] = 3600
        app.config['SECRET_KEY'] = 'Do not go gentle into that good night'
        app.config['FILESERVICE_UPLOAD_FOLDER'] = join_upload_dir('data/fileservice')
        app.config['FILESERVICE_THUMBNAIL_FOLDER'] = join_upload_dir('data/fileservice/thumbnail')
        app.config['FILESERVICE_MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
        app.tjwss = TJWSS(app.config['SECRET_KEY'],expires_in=app.config['TOKEN_EXPIRES_IN'])
        return app
