from flask import Blueprint,render_template,request,session,jsonify,current_app,flash,g
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
    #r = db.session.query(VolTime,func.sum(VolTime.time)).group_by(VolTime.stu_id).order_by(VolTime.time.desc())
    #cursor = db.session.execute("select name,faculty,stu_id,sum(time) from vol_time group by stu_id,name,time,faculty order by time desc limit 50")
    #res = cursor.fetchall()
    #data = [dict(zip(result.keys(),result)) for result in res]
    tr = {}#time result
    vlist = VolTime.query.filter(VolTime.stu_id!="0").all()
    for v in vlist:
        if v.stu_id not in tr:
            tr[v.stu_id] = {'time':0.0,'name':v.name,'faculty':v.faculty}
        try:
            tr[v.stu_id]['time'] += float(v.time)
        except:
            pass
            #current_app.logger.warn(v.time)
    topk = heapq.nlargest(50,tr,key=lambda x:tr[x]['time'])
    return render_template('vol_time_top.html',data=topk,tr=tr)
 


