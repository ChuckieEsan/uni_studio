from flask import Blueprint,current_app,session,send_file
from studio.utils.captcha_helper import _get_captcha_img,getcaptcha
import time
common = Blueprint("common",__name__,template_folder='templates',static_folder='static')#static folder and template folder are set here to avoid ambiguity

@common.route('/captcha')
def get_captcha_img():
    session['captcha_text'] = getcaptcha(current_app.config['CAPTCHA_LEN'])
    session['captcha_time'] = int(time.time())
    return send_file(_get_captcha_img(session['captcha_text']),mimetype='image/jpeg')