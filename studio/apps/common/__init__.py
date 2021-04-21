from flask import Blueprint,current_app,session,send_file,Response
from studio.utils.captcha_helper import _get_captcha_img,getcaptcha
from studio.interceptors import validate_captcha,CAPTCHA_COOKIE_KEY,CAPTCHA_NAMESPACE,CAPTCHA_TIMEOUT,CAPTCHA_VALID_FIELD
from studio.cache import cache
import time
import uuid
common = Blueprint("common",__name__,template_folder='templates',static_folder='static')#static folder and template folder are set here to avoid ambiguity


@common.route('/captcha')
def get_captcha_img():
    captcha_text = getcaptcha(current_app.config['CAPTCHA_LEN'])
    _uuid = uuid.uuid1()
    _c = str(_uuid).encode(encoding='utf-8')
    cache.set('{}:{}'.format(CAPTCHA_NAMESPACE,_uuid),captcha_text,timeout=CAPTCHA_TIMEOUT)
    resp:Response = send_file(_get_captcha_img(captcha_text),mimetype='image/jpeg')
    resp.set_cookie(CAPTCHA_COOKIE_KEY,_c,max_age=CAPTCHA_TIMEOUT,domain=current_app.config['SERVER_NAME'],httponly=True,secure=True)
    return resp

@common.route('/captcha/validate',methods=['GET','POST'])
@validate_captcha
def v_captcha():
    return 'ok'