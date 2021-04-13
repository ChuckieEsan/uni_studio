from flask import render_template,redirect,request,abort,g,url_for,current_app
from studio.models import db,UserRoles,UserUsers
from studio.apps.console import console
from sqlalchemy import func
import struct
@console.route('/user')
def user_show():
    roles = UserRoles.query.filter(UserRoles.delete == False).all()
    for role in roles:
        role.role_bit_bin = bin(role.role_bit)[2:]
    users = UserUsers.query.filter(UserUsers.delete == False).all()
    def and_op(a,b):
        return int(a) & int(b)
    r2 = db.session.query(UserRoles.role_bit,UserRoles.role_text,UserRoles.description,UserUsers.username)\
        .outerjoin(UserUsers,UserRoles.created_by==UserUsers.id).all()
    return render_template("user_manage.html",and_op=and_op,\
    roles=roles,users=users,title="用户管理",r2=r2,bin_op=bin) 

@console.route('/role',methods=['POST'])
def role_add():
    role_max = db.session.query(func.max(UserRoles.role_bit).label('role_bit')).one()
    i = 0
    if role_max.role_bit:
        while 1 << i <role_max.role_bit:
            i = i+1
    role_bit = 1 << (i+1)
    _u = UserRoles(role_bit = role_bit,role_text=request.values.get('role_text'),description=request.values.get('description'))
    db.session.add(_u)
    db.session.commit()
    return redirect(url_for('console.user_show')) 

@console.route('/update',methods=['POST'])
def role_update():
    roles = request.form.getlist('roles')
    id = request.form['id']
    user = UserUsers.query.filter(UserUsers.id==id).first()
    user.role_bits = 0
    for r in roles:
        user.role_bits |= int(r)
    db.session.commit()
    return redirect(url_for('console.user_show'))

@console.route('/user/crud',methods=['GET','POST','PUT','DELETE'])
def user_crud():
    target_class = UserUsers
    if request.method == "GET":
        users = target_class.query.all()
        # wip: figure out the actual data type
        print(getattr(target_class,'id').impl)
        return render_template('common_crud.html',
        data=users,_class=target_class,type=type,getattr=getattr)

    elif request.method=="POST":
        key = request.values.get('key')
        value = request.values.get('value')
        _id = request.values.get('id')
        if not key or not value:
            abort(500)
        data = target_class.query.filter(getattr(target_class,'id')==_id).first()
        if data:
            setattr(data,key,value)
            db.session.commit()
        return redirect(url_for('console.user_crud'))

# @console.route('/import')
# def imports():
#     import pymongo,time
#     MONGO_URL = "mongodb://admin:Bit_root_123@localhost:27017/?authSource=admin"
#     cli = pymongo.MongoClient(MONGO_URL)
#     userdb = cli['userservice2']
#     usertable = userdb['users']
#     roles = UserRoles.query.all()
#     for u in usertable.find():
#         _u = UserUsers(kwargs={
#             'username':u['username'],
#             'email':u['email'],
#             'password':u['password'],
#             'current_ip':u['ip'],
#             'last_login_ip':u['last_login_ip'],
#             'objid':str(u['_id']),
#             'role_bits':0
#         })
#         for r in roles:
#             if r.role_text in u['role']:
#                 _u.role_bits = _u.role_bits | r.role_bit
#         db.session.add(_u)
#     db.session.commit()
#     return 'ok'