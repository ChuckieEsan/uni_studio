from flask import Blueprint, render_template, request, jsonify, current_app, flash, g
from studio.models import db, VolTime
from studio.cache import cache
import os
import heapq
from sqlalchemy import func
vol_time = Blueprint("vol_time", __name__, template_folder="templates")


@vol_time.route('/', methods=["GET"])
def vol_time_home():
    return render_template("vol_time_index.html", title="志愿时长查询")


@vol_time.route('/', methods=['POST'])
def vol_time_search():
    resp = {"name": "", "dataSheet": []}
    name = request.values.get('name')
    stu_id = request.values.get('stu_id')

    cursor = db.session.execute(
        "select * from vol_time_old where name = :name and stu_id = :stu_id", {'name': name, 'stu_id': stu_id})
    # "C:\Users\Administrator\Anaconda3\Lib\site-packages\sqlalchemy\engine\result.py"
    res = cursor.fetchall()
    set_idsOld = set([result['id'] for result in res])

    cursor = db.session.execute(
        "select * from vol_time where name = :name and stu_id = :stu_id", {'name': name, 'stu_id': stu_id})
    res = cursor.fetchall()
    data = [dict(zip(result.keys(),  result)) for result in res]
    resp['name'] = name
    for d in data:
        resp['dataSheet'].append({"activity_DATE": str(d['activity_DATE']), 'name': d['name'],
                                  'faculty': d['faculty'], 'stu_id': d['stu_id'],
                                  'duration': d['duration'], 'activity_faculty': d['activity_faculty'],
                                  'activity_name': d['activity_name'], 'duty_person': d['duty_person'],
                                  'queryNewly': 0 if d['id'] in set_idsOld else 1})
    set_idsNow = set([d['id'] for d in data])
    resp['err_queryLost'] = 1 if len(
        set_idsOld.difference(set_idsNow)) > 0 else 0

    cursor = db.session.execute(
        "SELECT `name` FROM vol_time WHERE stu_id = :stu_id GROUP BY `name`", {'stu_id': stu_id})
    res = cursor.fetchall()
    resp['num_sameID'] = len(res)

    cursor = db.session.execute(
        "SELECT stu_id FROM vol_time WHERE `name` = :name GROUP BY stu_id", {'name': name})
    res = cursor.fetchall()
    resp['num_sameName'] = len(res)

    return jsonify(resp)


@vol_time.route('/top')
@cache.memoize(2000)
def get_top():
    sql_str = "SELECT CONCAT(LEFT(stu_id,6),'***') AS one_id, MAX(`name`) AS one_name,\
SUM(duration) AS dur_sum FROM `vol_time` GROUP BY `stu_id` ORDER BY dur_sum DESC LIMIT 1,50"
    cursor = db.session.execute(sql_str)
    res = cursor.fetchall()
    data = [dict(zip(result.keys(), result)) for result in res]
    return render_template('vol_time_top.html', title="排行榜", data=data)
