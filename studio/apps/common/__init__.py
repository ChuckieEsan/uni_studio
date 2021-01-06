from flask import Blueprint,current_app,session,send_file
from studio.utils.captcha_helper import _get_captcha_img
from studio.interceptors import set_captcha
common = Blueprint("common",__name__,template_folder='templates',static_folder='static')#static folder and template folder are set here to avoid ambiguity

@common.route('/captcha')
@set_captcha
def get_captcha_img():
    return send_file(_get_captcha_img(session['captcha_text']),mimetype='image/jpeg')