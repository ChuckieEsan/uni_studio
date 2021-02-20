from flask import Blueprint,render_template,request,jsonify,session,redirect
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
        session['id'] = user.id
        session['email'] = user.email
        session['role_bits'] = user.role_bits
        return jsonify({"success":True})
    return jsonify({"success":False,"details":"用户名或密码错误"})  

@users.route('/logout')
def users_logout():
    return 'out'