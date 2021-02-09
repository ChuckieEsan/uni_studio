from flask import Blueprint,render_template,request,session,jsonify
from studio.models import db
from pymysql.cursors import DictCursor
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
        r['all_time'] = r['all_time'] + float(d['time'])
    return jsonify(r)
