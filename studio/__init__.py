import logging
import os

from .interceptors import global_interceptor
from .utils.error_helper import error_handler
from .utils.ver_helper import get_ver
from studio.cos import url_for_cos
from studio.utils import setup_roles

from flask import Flask, redirect
from .cache import cache
from .utils.log import LiveLog
from flask_bootstrap import Bootstrap  # for flask-file-uploader | fileservice
from flask_migrate import Migrate
from flask_hcaptcha import hCaptcha

from .test import tests
from .apps.fileservice.app import app as fileserviceapp
from .apps.staticfile.app import app as staticfileapp
from .apps.vote import vote as voteapp
from .api import postcardapp
from .apps.issues import issues as issuesapp
from .apps.common import common as commonfileapp
from .apps.console import console as consoleapp
from .apps.vol_time import vol_time as vol_timeapp
from .apps.users import users as usersapp
from .apps.enroll import enroll as enrollapp
from .apps.h5 import h5 as h5app
from .apps.chat import chat as chatapp

from itsdangerous import TimedJSONWebSignatureSerializer as TJWSS


def create_app():
    app = Flask(__name__)

    # set up logger
    try:
        os.mkdir('log')
    except:
        pass
    handler = logging.FileHandler('log/service.log')
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        '%(levelname)s - %(asctime)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    # set up global interceptor
    app.before_request(global_interceptor)
    for i in (400, 401, 404, 403, 500, 503):
        app.register_error_handler(i, error_handler)
    with app.app_context():
        from studio.models import db
        from config import Config
        app.config.from_object(Config())

        print('---- debug = {} ----'.format(app.config.get('DEBUG')))
        app.add_template_global(get_ver)
        app.add_template_global(url_for_cos)
        app.before_first_request(setup_roles)

        db.init_app(app)
        cache.init_app(app)
        Bootstrap(app)
        Migrate(app, db)

        app.live_log = LiveLog()
        app.hcaptcha = hCaptcha()
        app.hcaptcha.init_app(app)

        app.add_url_rule(
            '/', view_func=lambda: redirect(app.config["HOMEPAGE_URL"]))
        app.register_blueprint(tests)
        app.register_blueprint(fileserviceapp, url_prefix='/fileservice')
        app.register_blueprint(staticfileapp, url_prefix='/staticfile')
        app.register_blueprint(voteapp, url_prefix='/vote')
        app.register_blueprint(postcardapp, url_prefix='/postcard')
        app.register_blueprint(issuesapp, url_prefix="/issues")
        app.register_blueprint(commonfileapp, url_prefix="/common")
        app.register_blueprint(consoleapp, url_prefix="/console")
        app.register_blueprint(vol_timeapp, url_prefix="/vol_time")
        app.register_blueprint(usersapp, url_prefix="/user")
        app.register_blueprint(enrollapp, url_prefix="/enroll")
        app.register_blueprint(h5app, url_prefix="/h5")
        app.register_blueprint(chatapp, url_prefix='/chat')

        app.tjwss = TJWSS(app.config['SECRET_KEY'],
                          expires_in=app.config['TOKEN_EXPIRES_IN'])
        return app
