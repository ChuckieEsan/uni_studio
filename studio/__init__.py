import os
from flask import Flask,Request
from flask_bootstrap import Bootstrap#for flask-file-uploader | fileservice
from .test import tests
from .fileservice.app import app as fileserviceapp
from .vote import vote
from .utils.dir_helper import join_upload_dir
def create_app():
    app = Flask(__name__)
    with app.app_context():
        Bootstrap(app)

        from studio.models import db
    
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
        db.init_app(app)
        db.create_all()

        app.register_blueprint(tests)
        app.register_blueprint(fileserviceapp)
        app.register_blueprint(vote)
        app.config['SECRET_KEY'] = 'hard to guess string'
        app.config['FILESERVICE_UPLOAD_FOLDER'] = join_upload_dir('data/')
        app.config['FILESERVICE_THUMBNAIL_FOLDER'] = join_upload_dir('data/thumbnail/')
        app.config['FILESERVICE_MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
        return app