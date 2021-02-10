from flask import Blueprint,render_template,request,session,jsonify,current_app,flash,g
from studio.interceptors import session_required,roles_required
from studio.models import db
import os
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

def get_rows():
    cursor = db.session.execute("select count(*) from vol_time")
    res = cursor.fetchall()
    count = res[0][0]
    return count

@vol_time.route('/update',methods=['GET'])
@session_required('/console/')
@roles_required(['super_admin','vol_time_admin'])
def vol_time_update():
    return render_template("vol_time_update.html",count=get_rows())

@vol_time.route('/update',methods=['POST'])
@session_required('/console/')
@roles_required(['super_admin','vol_time_admin'])
def do_vol_time_update():
    fname = request.values.get('fileIndex')
    coverall = request.values.get('coverall') !=None
    files = [f for f in os.listdir(os.path.join(current_app.config['FILESERVICE_UPLOAD_FOLDER'],g._id))\
        if os.path.isfile(os.path.join(current_app.config['FILESERVICE_UPLOAD_FOLDER'],g._id,f))]
    if fname not in fname:
        flash('无效的文件')
        return render_template("vol_time_update.html",count=get_rows())
    flash('more')
    return render_template("vol_time_update.html",count=get_rows())