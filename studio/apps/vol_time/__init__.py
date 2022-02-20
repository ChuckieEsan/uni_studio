from flask import Blueprint, render_template, request, jsonify, current_app, flash, g
from studio.models import db, VoltimeOld, Voltime, VoltimeDupname
from studio.utils.cache import cache
import os
import heapq
from sqlalchemy import func
vol_time = Blueprint("vol_time", __name__, template_folder="templates")

import time
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib


@vol_time.route('/test/<tet>')
def vol_time_test(tet: str):
    time_start = time.time()
    hash1 = hashlib.sha512(tet.encode("utf-8")).hexdigest()
    hash2 = generate_password_hash(hash1)
    timea1 = time.time() - time_start
    return hash2 + '\n' + str(timea1) + "\n" + hash1 + "fff" if check_password_hash(hash2,hash1) else "no"


@vol_time.route('/', methods=["GET"])
def vol_time_home():
    lastDate = db.session.query(Voltime.activity_DATE)\
        .order_by(Voltime.activity_DATE.desc()).first()[0]
    lastDate = lastDate.strftime('%Y-%m-%d')
    return render_template("vol_time_index.html", title="志愿时长查询", lastDate=lastDate)


@vol_time.route('/', methods=['POST'])
def vol_time_search():
    req_name = request.values.get('name')
    req_stu_id = request.values.get('stu_id')

    # cursor = db.session.execute("select * from vol_time_old where name = :name and stu_id = :stu_id", {'name': name, 'stu_id': stu_id})
    # "C:\Users\Administrator\Anaconda3\Lib\site-packages\sqlalchemy\engine\result.py"
    # res = cursor.fetchall()
    results = db.session.query(VoltimeOld.id)\
        .filter(VoltimeOld.stu_id == req_stu_id, VoltimeOld.name == req_name).all()
    set_idsOld = set([result[0] for result in results])

    voltimes = db.session.query(Voltime)\
        .filter(Voltime.stu_id == req_stu_id, Voltime.name == req_name)\
        .order_by(Voltime.activity_DATE.desc()).all()
    voltimeList = []
    for voltime in voltimes:
        voltime = voltime.__dict__
        voltime.pop('_sa_instance_state')
        voltime['activity_DATE'] = voltime['activity_DATE'].strftime(
            '%Y-%m-%d') if voltime['activity_DATE'].year > 2005 else voltime['activity_date_str']
        voltime['queryNewly'] = 0 if voltime['id'] in set_idsOld or voltime['id'] > 100000 else 1
        voltimeList.append(voltime)

    set_idsNow = set([voltime['id'] for voltime in voltimeList])
    err_queryLost = 1 if len(set_idsOld.difference(set_idsNow)) > 0 else 0

    num_sameID = db.session.query(Voltime.name).filter(Voltime.stu_id == req_stu_id).group_by(Voltime.name).count()
    num_sameName = db.session.query(Voltime.stu_id).filter(Voltime.name == req_name).group_by(Voltime.stu_id).count()
    dupName = db.session.query(VoltimeDupname).filter(VoltimeDupname.name == req_name).first()
    num_dupName = 1 if dupName is None else dupName.dupNum
    return jsonify({
        "name": req_name, "dataSheet": voltimeList, "num_sameID": num_sameID, "num_sameName": num_sameName,
        "num_dupName": num_dupName, "err_queryLost": err_queryLost
    })


@vol_time.route('/top')
@cache.memoize(2000)
def get_top():
    sql_str = "SELECT CONCAT(LEFT(stu_id,6),'***') AS one_id, MAX(`name`) AS one_name,\
SUM(duration) AS dur_sum FROM `vol_time` GROUP BY `stu_id` ORDER BY dur_sum DESC LIMIT 1,50"

    cursor = db.session.execute(sql_str)
    res = cursor.fetchall()
    data = [dict(zip(result.keys(), result)) for result in res]
    return render_template('vol_time_top.html', title="排行榜", data=data)
