import os
from flask import Flask,Request
from flask_bootstrap import Bootstrap#for flask-file-uploader | fileservice
from .test import tests
from .fileservice.app import app as fileserviceapp
from .vote import vote as voteapp
from .api import postcardapp
from .issues import issues as issuesapp
from .utils.dir_helper import join_upload_dir
import redis
#r = redis.Redis(host='localhost',port=6379,decode_responses=True,password='Bit_redis_123')

def create_app():
    app = Flask(__name__)
    with app.app_context():
        Bootstrap(app)

        from studio.models import db
    
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        #db.drop_all()
        db.create_all()

        app.register_blueprint(tests)
        app.register_blueprint(fileserviceapp)
        app.register_blueprint(voteapp)
        app.register_blueprint(postcardapp)
        app.register_blueprint(issuesapp)
        #app.config['SERVER_NAME'] = 'dutbit.com'
        app.config['SECRET_KEY'] = 'Do not go gentle into that good night'
        app.config['FILESERVICE_UPLOAD_FOLDER'] = join_upload_dir('data/')
        app.config['FILESERVICE_THUMBNAIL_FOLDER'] = join_upload_dir('data/thumbnail/')
        app.config['FILESERVICE_MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
        return app