from flask import Blueprint,render_template,request,jsonify,current_app,flash,g
from studio.models import db,VolTime
from studio.cache import cache
import os
import heapq
from sqlalchemy import func
vol_time = Blueprint("vol_time",__name__,template_folder="templates")

@vol_time.route('/',methods=["GET"])
def vol_time_home():
    return render_template("vol_time_index.html",title="志愿时长查询")

@vol_time.route('/',methods=['POST'])
def vol_time_search():
    r = {"name":"","data":"","all_time":0}
    name = request.values.get('name')
    number = request.values.get('number')
    cursor = db.session.execute("select * from vol_time where name = :name\
     and stu_id = :stuid",{'name':name,'stuid':number})
    res = cursor.fetchall()
    data = [dict(zip(result.keys(),result)) for result in res]
    r['name'] = name
    for d in data:
        r['data'] = r['data']+"<tr> <td><p>{}</p></td> <td><p>{}</p></td> <td><p>{}</p></td> <td><p>{}</p></td>\
        <td><p>{}</p></td> <td><p>{}</p></td> <td><p>{}</p></td> <td><p>{}</p></td> </tr>"\
        .format(d['activity_time'],d['name'],d['faculty'],d['stu_id'],d['time'],d['activity_faculty'],\
        d['activity_name'],d['duty_person'])
        try:
            r['all_time'] = r['all_time'] + float(d['time'])
        except:
            pass
    return jsonify(r)

@vol_time.route('/top')
@cache.memoize(2000)
def get_top():
    #约200ms，会选出重复的stu_id!!!
    sql = """ 
    select v1.name,v1.faculty,v1.stu_id,v2.STIME from `vol_time`  as v1  INNER JOIN (
	SELECT  SUM(time) as STIME,`stu_id`  from `vol_time` GROUP BY `stu_id` ORDER BY STIME DESC LIMIT 1,51
) AS v2 on v1.stu_id = v2.stu_id GROUP BY v1.stu_id,v1.name,v1.faculty ORDER BY v2.STIME DESC;
    """
    cursor = db.session.execute(sql)
    res = cursor.fetchall()
    data = [dict(zip(result.keys(),result)) for result in res]
    stu_id_map = set([])
    result = []
    for d in data:
        if d['stu_id'] not in stu_id_map:
            stu_id_map.add(d['stu_id'])
            result.append(d)
    return render_template('vol_time_top.html',data=result)
 


