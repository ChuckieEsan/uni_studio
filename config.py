from studio.utils.dir_helper import join_upload_dir
import os
import socket
from datetime import timedelta

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)


class Config():
    DEBUG = False if ip == '172.31.240.127' else True
    VERSION = os.popen('git rev-parse --short HEAD').read()
    SERVER_NAME = 'vm.dutbit.com' if DEBUG else 'www.dutbit.com'

    # DB Config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    if (not DEBUG) and 'mysql+pymysql' not in SQLALCHEMY_DATABASE_URI:
        raise EnvironmentError("No db connection uri provided")
        exit(-1)

    # Captcha Config
    CAPTCHA_LEN = 4

    # JWT TOKEN Config
    TOKEN_EXPIRES_IN = 3600
    SECRET_KEY = 'Do not go gentle into that good night'

    HOMEPAGE_URL = "https://wp.dutbit.com/wp20/"

    # Fileservice Config
    FILESERVICE_UPLOAD_FOLDER = join_upload_dir('data/fileservice')
    FILESERVICE_THUMBNAIL_FOLDER = join_upload_dir(
        'data/fileservice/thumbnail')
    FILESERVICE_MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    MAIL_PASS = os.environ.get('MAIL_PASS')

    HCAPTCHA_SITE_KEY = os.environ.get('HCAPTCHA_SITE_KEY')
    HCAPTCHA_SECRET_KEY = os.environ.get('HCAPTCHA_SECRET_KEY')
    HCAPTCHA_ENABLED = not DEBUG

    if DEBUG:
        SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=5)
