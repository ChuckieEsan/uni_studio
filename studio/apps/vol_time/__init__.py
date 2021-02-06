from flask import Blueprint,render_template,request,session
from studio.models import db
vol_time = Blueprint("vol_time",__name__,template_folder="templates")

@vol_time.route('/',methods=["GET"])
def vol_time_home():
    return render_template("index.html",title="志愿时长查询")

@vol_time.route('/',methods=['POST'])
def vol_time_search():
    name = request.values.get('name')
    number = request.values.get('number')
    cursor = db.session.execute('select * from vol_time.vt where name = ? and stu_id = ?',params={"name":name,"stu_id":number})
    res = cursor.fetch_all()
    print(res)
    return '1'