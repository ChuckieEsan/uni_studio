from flask import Blueprint, render_template, request, jsonify, current_app, flash, g
from studio.models import db, VolTime_old, VolTime, VolTime_dupName
from studio.cache import cache
import os
import heapq
from sqlalchemy import func
vol_time = Blueprint("vol_time", __name__, template_folder="templates")


@vol_time.route('/', methods=["GET"])
def vol_time_home():
    lastDate = db.session.query(VolTime.activity_DATE)\
        .order_by(VolTime.activity_DATE.desc()).first()[0]
    lastDate = lastDate.strftime('%Y-%m-%d')
    return render_template("vol_time_index.html", title="志愿时长查询", lastDate=lastDate)


@vol_time.route('/', methods=['POST'])
def vol_time_search():
    req_name = request.values.get('name')
    req_stu_id = request.values.get('stu_id')

    # cursor = db.session.execute("select * from vol_time_old where name = :name and stu_id = :stu_id", {'name': name, 'stu_id': stu_id})
    # "C:\Users\Administrator\Anaconda3\Lib\site-packages\sqlalchemy\engine\result.py"
    # res = cursor.fetchall()
    results = db.session.query(VolTime_old.id)\
        .filter(VolTime_old.stu_id == req_stu_id, VolTime_old.name == req_name).all()
    set_idsOld = set([result[0] for result in results])

    volTimes = db.session.query(VolTime)\
        .filter(VolTime.stu_id == req_stu_id, VolTime.name == req_name)\
        .order_by(VolTime.activity_DATE.desc()).all()
    volTimeList = []
    for volTime in volTimes:
        volTime = volTime.__dict__
        volTime.pop('_sa_instance_state')
        volTime['activity_DATE'] = volTime['activity_DATE'].strftime(
            '%Y-%m-%d') if volTime['activity_DATE'].year > 2005 else volTime['activity_date_str']
        volTime['queryNewly'] = 0 if volTime['id'] in set_idsOld or volTime['id'] > 100000 else 1
        volTimeList.append(volTime)

    set_idsNow = set([volTime['id'] for volTime in volTimeList])
    err_queryLost = 1 if len(set_idsOld.difference(set_idsNow)) > 0 else 0

    num_sameID = db.session.query(VolTime.name)\
        .filter(VolTime.stu_id == req_stu_id).group_by(VolTime.name).count()
    num_sameName = db.session.query(VolTime.stu_id)\
        .filter(VolTime.name == req_name).group_by(VolTime.stu_id).count()

    return jsonify({"name": req_name, "dataSheet": volTimeList,
                    "num_sameID": num_sameID, "num_sameName": num_sameName, "err_queryLost": err_queryLost})


@vol_time.route('/top')
@cache.memoize(2000)
def get_top():
    sql_str = "SELECT CONCAT(LEFT(stu_id,6),'***') AS one_id, MAX(`name`) AS one_name,\
SUM(duration) AS dur_sum FROM `vol_time` GROUP BY `stu_id` ORDER BY dur_sum DESC LIMIT 1,50"
    cursor = db.session.execute(sql_str)
    res = cursor.fetchall()
    data = [dict(zip(result.keys(), result)) for result in res]
    return render_template('vol_time_top.html', title="排行榜", data=data)
