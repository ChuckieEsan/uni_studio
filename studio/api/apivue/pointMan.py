from flask import Blueprint, jsonify, request, current_app
from studio.models.points import db, Points

point_man = Blueprint('point_man', __name__, url_prefix='/point-man')  # 创建二级蓝图


@point_man.route('/row-total')
def r_get_rows_total():
    return jsonify({'total': get_rows_total()})


@point_man.route('/get-records')
def vol_time_data():
    pageNumber = int(request.values.get('current'))
    pageSize = 30 if request.values.get('pageSize') is None else int(request.values.get('pageSize'))

    searchText: str = request.values.get('searchText')
    sameList = []
    if searchText == '' or searchText is None:
        PointsQuery = Points.query
    elif searchText.isdigit():
        PointsQuery = Points.query.filter(Points.stu_id == searchText)
        sameList = db.session.query(Points.name).filter(Points.stu_id == searchText).group_by(Points.name).all()
    else:
        PointsQuery = Points.query.filter(Points.name == searchText)
        sameList = db.session.query(Points.stu_id).filter(Points.name == searchText).group_by(Points.stu_id).all()

    lstPoints: list[Points] = PointsQuery.order_by(Points.id.desc())\
        .paginate(pageNumber, per_page=pageSize, error_out=False).items
    lstRows = []
    for rowPoints in lstPoints:
        rowPoints = rowPoints.__dict__
        rowPoints.pop('_sa_instance_state')
        lstRows.append(rowPoints)
        # print(json.dumps(Points))
    return jsonify({"total": PointsQuery.count(), "rows": lstRows, "sameList": [item[0] for item in sameList]})


@point_man.route('/update-by-array', methods=['POST'])
def r_update_by_array():
    lstRecords = request.get_json()
    try:
        for record in lstRecords:
            resPoints = Points.query.filter_by(name=record['name'], stu_id=record['stu_id']).one_or_none()
            if resPoints is None:
                print("new")
                rowPointsNew = Points(name=record['name'], stu_id=record['stu_id'], points=record['points'])
                db.session.add(rowPointsNew)
            else:
                print("update")
                resPoints.points = record['points']
                db.session.add(resPoints)

        db.session.commit()
        current_app.logger.info('load data ok')
        return '操作成功'
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return '操作失败'


def get_rows_total():
    return db.session.execute('select count(*) from points').scalar()