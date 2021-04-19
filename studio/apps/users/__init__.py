from flask import Blueprint,render_template,request,jsonify,g,redirect,Response,current_app
from flask.helpers import url_for
from studio.models import db,UserUsers
users = Blueprint("users",__name__,template_folder="templates",static_folder="static")

@users.route('/')
def users_entrypoint():
    return render_template('users_index.html',title="DUTBIT SSO")

@users.route('/register',methods=['POST'])
def users_register():
    user = UserUsers(kwargs=request.get_json())
    db.session.add(user)
    db.session.commit()
    return jsonify({"success":True}) 

@users.route('/login',methods=['POST'])
def users_login():
    data = request.get_json()
    user = UserUsers.query.filter(UserUsers.email==str(data.get('email')).strip())\
    .filter(UserUsers.password==str(data.get('password')).strip()).first()
    if user:
        info = {'id':user.id}
        resp:Response = jsonify({"success":True})
        token = current_app.tjwss.dumps(info).decode()
        resp.set_cookie('token',token,max_age=current_app.config['EXPIRES_IN'],
            domain=current_app.config['SERVER_NAME'],secure=True,httponly=True)
        return resp
    return jsonify({"success":False,"details":"用户名或密码错误"})  

@users.route('/logout')
def users_logout():
    return redirect(url_for('users.users_entrypoint'))