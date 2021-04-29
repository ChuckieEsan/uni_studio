from flask import Blueprint, current_app, send_file, Response
from studio.utils.captcha_helper import _get_captcha_img, getcaptcha
from studio.interceptors import validate_captcha, CAPTCHA_COOKIE_KEY, CAPTCHA_NAMESPACE, CAPTCHA_TIMEOUT, CAPTCHA_VALID_FIELD
from studio.cache import cache
from studio.models import GlobalNotifications
import uuid
import datetime
# static folder and template folder are set here to avoid ambiguity
common = Blueprint("common", __name__,
                   template_folder='templates', static_folder='static')


@common.route('/captcha')
def get_captcha_img():
    captcha_text = getcaptcha(current_app.config['CAPTCHA_LEN'])
    _uuid = uuid.uuid1()
    _c = str(_uuid).encode(encoding='utf-8')
    cache.set('{}:{}'.format(CAPTCHA_NAMESPACE, _uuid),
              captcha_text, timeout=CAPTCHA_TIMEOUT)
    resp: Response = send_file(_get_captcha_img(
        captcha_text), mimetype='image/jpeg')
    resp.set_cookie(CAPTCHA_COOKIE_KEY, _c, max_age=CAPTCHA_TIMEOUT,
                    domain=current_app.config['SERVER_NAME'], httponly=True, secure=True)
    return resp


@common.route('/captcha/validate', methods=['GET', 'POST'])
@validate_captcha
def v_captcha():
    return 'ok'


@common.route('/notification/global')
def get_global_notification():
    noti = GlobalNotifications.query.filter(
        GlobalNotifications.valid_until > datetime.datetime.now()).order_by(GlobalNotifications.valid_until.desc()).first()
    html = """
    <div class="alert alert-warning alert-dismissible fade show" role="alert">
      {}
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
    </button>
    </div>
    """.format(noti.text)
    result = "" if not noti else html
    return result
