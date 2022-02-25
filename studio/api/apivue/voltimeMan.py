from flask import Blueprint, jsonify, request, current_app
from studio.models import db, VoltimeOld, Voltime, VoltimeDupname
import re

voltime_man = Blueprint('voltime_man', __name__, url_prefix='/voltime-man')


@voltime_man.route('/row-total')
def r_get_rows_total():
    return jsonify({'total': get_rows_total()})


@voltime_man.route('/get-records')
def vol_time_data():
    pageNumber = int(request.values.get('current'))
    pageSize = 30 if request.values.get('pageSize') is None else int(request.values.get('pageSize'))

    searchText: str = request.values.get('searchText')
    sameList = []
    if searchText == '' or searchText is None:
        voltimeQuery = Voltime.query
    elif searchText.isdigit():
        voltimeQuery = Voltime.query.filter(Voltime.stu_id == searchText)
        sameList = db.session.query(Voltime.name).filter(Voltime.stu_id == searchText).group_by(Voltime.name).all()
    else:
        voltimeQuery = Voltime.query.filter(Voltime.name == searchText)
        sameList = db.session.query(Voltime.stu_id).filter(Voltime.name == searchText).group_by(Voltime.stu_id).all()

    voltimes: list[Voltime] = voltimeQuery.order_by(Voltime.activity_DATE.desc())\
        .paginate(pageNumber, per_page=pageSize, error_out=False).items
    voltimeList = []
    for voltime in voltimes:
        voltime = voltime.__dict__
        voltime.pop('_sa_instance_state')
        voltime['activity_DATE'] = voltime['activity_DATE'].strftime('%Y-%m-%d')
        voltimeList.append(voltime)
        # print(json.dumps(voltime))
    return jsonify({"total": voltimeQuery.count(), "rows": voltimeList, "sameList": [item[0] for item in sameList]})


@voltime_man.route('/update-by-array', methods=['POST'])
def r_update_by_array():
    lstRecords = request.get_json()
    for record in lstRecords:
        if len(record) != 12:
            return '操作失败，数据异常'
        if re.match(r'^\d+$', record[4]) is None:
            return '操作失败，数据异常'
        if re.match(r'^(\d{1,3}|\d{1,3}\.\d+)$', record[5]) is None:
            return '操作失败，数据异常'
        if re.match(r'^\d{4}\/\d{1,2}\/\d{1,2}$', record[9]) is None:
            return '操作失败，数据异常'

    nRows_old = get_rows_total()
    try:
        for record in lstRecords:
            rowVoltime = Voltime(name=record[1],
                                 sex=record[2],
                                 faculty=record[3],
                                 stu_id=record[4],
                                 duration=record[5],
                                 activity_name=record[6],
                                 activity_faculty=record[7],
                                 team=record[8],
                                 activity_DATE=record[9],
                                 duty_person=record[10],
                                 remark=record[11])
            db.session.add(rowVoltime)
            db.session.commit()
        current_app.logger.info('load data ok')
        return '操作成功，插入' + (str(get_rows_total() - nRows_old)) + '条新数据'
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return '操作失败，原有' + str(nRows_old) + '条，现有' + str(get_rows_total()) + '条'


def get_rows_total():
    return db.session.execute('select count(*) from voltime').scalar()