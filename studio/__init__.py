import redis
try:
    r = redis.Redis(host='localhost',port=6379,decode_responses=True,password='Bit_redis_123')
except Exception as e:
    print(e)
    r = None
    
import os
import socket
from flask import Flask, Request
from flask_bootstrap import Bootstrap  # for flask-file-uploader | fileservice
from .test import tests
from .fileservice.app import app as fileserviceapp
from .vote import vote as voteapp
from .api import postcardapp
from .issues import issues as issuesapp
from .utils.dir_helper import join_upload_dir


hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

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
            app.config['DEBUG'] = True
            app.config['SERVER_NAME'] = 'dutbit.com'
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
            app.config['SUBDOMAINS'] = subdomains['PRODUCTION']
            if 'mysql+pymysql' not in app.config['SQLALCHEMY_DATABASE_URI']:
                raise EnvironmentError("No db connection uri provided")
                exit(-1)
        else:
            print('------ starting service in development ------')
            app.config['DEBUG'] = False
            app.config['SERVER_NAME'] = '127.0.0.1:5000'
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
            app.config['SUBDOMAINS'] = subdomains['DEVELOPMENT']

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        # db.drop_all()
        db.create_all()
        app.register_blueprint(tests)
        app.register_blueprint(fileserviceapp)
        app.register_blueprint(voteapp,url_prefix='/vote',subdomain=app.config['SUBDOMAINS']['www'])
        app.register_blueprint(postcardapp)
        app.register_blueprint(issuesapp,url_prefix="/issues",subdomain=app.config['SUBDOMAINS']['www'])
        #app.config['SERVER_NAME'] = 'dutbit.com'
        app.config['SECRET_KEY'] = 'Do not go gentle into that good night'
        app.config['FILESERVICE_UPLOAD_FOLDER'] = join_upload_dir('data/')
        app.config['FILESERVICE_THUMBNAIL_FOLDER'] = join_upload_dir('data/thumbnail/')
        app.config['FILESERVICE_MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
        return app
