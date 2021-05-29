from flask import Blueprint, request
from flask.json import jsonify
from studio.models import GlobalNotifications
import datetime
import json
# static folder and template folder are set here to avoid ambiguity
common = Blueprint("common", __name__,
                   template_folder='templates', static_folder='static')


@common.route('/notification/global')
def get_global_notification():
    lim = []
    try:
        views = json.decode(request.values.get('viewed_noti'))
        for v in views:
            lim.append(int(v))
    except:
        pass
    noti = GlobalNotifications.query.filter(
        GlobalNotifications.valid_until > datetime.datetime.now())\
        .filter(GlobalNotifications.id.notin_(lim))\
        .order_by(GlobalNotifications.valid_until.desc()).all()
    result = []
    path = str(request.values.get('path'))
    for n in noti:
        if path.startswith(n.path):
            result.append({'id': n.id, 'text': n.text})
    return jsonify(result)
