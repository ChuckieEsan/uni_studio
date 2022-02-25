from flask import Blueprint, jsonify, request
from studio.models import db, Points

point = Blueprint('point', __name__, url_prefix='/point')  # 创建二级蓝图


@point.route('/', methods=['POST'])
def pointsQuery():
    dictReq = request.get_json()
    resPoints: Points = Points.query.filter_by(stu_id=dictReq['stu_id'], name=dictReq['name']).one_or_none()
    if resPoints is not None:
        return jsonify({'name': dictReq['name'], 'stu_id': dictReq['stu_id'], 'points': resPoints.points})
    else:
        return jsonify({'error': 'error'})
