#coding=utf-8
from flask import Flask,request,render_template,redirect,Blueprint,url_for,jsonify,session,make_response
from flask_sqlalchemy import SQLAlchemy
import pymysql,datetime,time,json,random,hashlib
from PIL import Image
from var_dump import var_dump
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSS
app = Flask(__name__)

EXPIRE_TIME = 60000
tjwss = TJWSS(app.config['SECRET_KEY'],expires_in=EXPIRE_TIME)
db = SQLAlchemy(app)
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    email = db.Column(db.String(80), nullable=True, unique=True)
    #role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(256), nullable=True)
    confirmed = db.Column(db.Boolean, default=False)
    reg_time = db.Column(db.Integer)
    log_time = db.Column(db.Integer)
    token = db.Column(db.String(40),nullable=True,unique=True)
    expire_time = db.Column(db.Integer,nullable=True)
    ip = db.Column(db.String(50),nullable=True)
    def __init__(self,email,password_hash,username):
        if username == None:
            username = ''
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.reg_time = int(time.time()) 

class Notes(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    create_time = db.Column(db.Integer,nullable=True)
    update_time = db.Column(db.Integer,nullable=True)
    query_key = db.Column(db.Text,nullable=True)
    tags = db.Column(db.Text,nullable=True)
    content = db.Column(db.Text,nullable=True)
    front = db.Column(db.Boolean,nullable=True)
    alert = db.Column(db.Boolean,nullable=True)
    alert_time = db.Column(db.Integer,nullable=True)
    uid = db.Column(db.String(33),nullable=False)
    def __init__(self,user_id,content,query_key,tags,uid,front=False,alert=False,alert_time=0):
        self.content = content
        self.user_id = user_id
        self.query_key = query_key
        self.tags = tags
        self.create_time = int(time.time())
        self.uid = uid
        self.front = front
        self.alert = alert
        self.alert_time = alert_time


@app.route('/mynote/user',methods=['GET','PUT','POST','DELETE'])
def user():
    msg = {'success':0,'data':'','code':0,'detail':''}
    if request.method == 'POST':#register
        #validate input
        data = request.get_data()
        json_data = json.loads(data.decode("utf-8"))
        username = json_data.get('username')
        password_hash = json_data.get('password_hash')
        email = json_data.get('email')
        captcha = json_data.get('captcha')
        print(username)
        new_user = Users(email,password_hash,username)
        try:
            db.session.add(new_user)
            db.session.commit()
            msg['success'] =1;msg['data'] = '注册成功';msg['code'] = 1001
        except Exception as e:
            db.session.rollback()
            msg['data'] = '用户名已存在';msg['code'] = 3;msg['detail'] = repr(e)
        return jsonify(msg)
    elif request.method == 'GET':# validate token before response --------EXpects token input.
        token = request.headers.get('Authorization')
        print(token)
        try:
            data = tjwss.loads(token)
            msg['success'] =1; msg['code'] = 1001; msg['data'] = data; 
        except Exception as e:
            msg['code'] = 5; msg['detail'] = repr(e);msg['data'] ='token expired.'
        return jsonify(msg)
    elif request.method == 'DELETE':#expects token input to delete user.
        msg['code'] = -1 
        msg['data'] = 'unexpected input'  
        status_code = 500
        response = make_response(json.dumps(msg), status_code)
        response.headers["Content-Type"] = "application/json"
        return response
    elif request.method == 'PUT':#expects token input and updates user info.
        msg['code'] = -1 
        msg['data'] = 'unexpected input'  
        status_code = 500
        response = make_response(json.dumps(msg), status_code)
        response.headers["Content-Type"] = "application/json"
        return response
    '''
    else:
        msg['code'] = -1 
        msg['data'] = 'unexpected input'  
        status_code = 500
        response = make_response(json.dumps(msg), status_code)
        response.headers["Content-Type"] = "application/json"
        return response
'''
def checkauth():
    token = request.headers.get('Authorization')
    if token==None:
        return (0,'access denied')
    try:
        data = tjwss.loads(token)
        return (1,data) 
    except Exception as e:
        print(e)
        return (0,'token expired')
@app.route('/mynote/timeline',methods=['GET'])
def notes_timeline():
    msg = {'success':0,'data':{},'code':0,'detail':{}}
    auth = checkauth()
    if auth[0] == 0:
        status_code = 403
        msg['data'] = auth[1]
        response = make_response(json.dumps(msg), status_code)
        response.headers["Content-Type"] = "application/json"
        return response
    else: 
        userinfo = auth[1]
    if request.method=='GET':
        start = request.values.get('start')
        end = request.values.get('end')
        user_id = userinfo['id']
        info = Notes.query.filter(Notes.user_id==user_id).filter(Notes.alert_time>=start).filter(Notes.alert_time<=end).all()
        a = []
        for u in info:
            u = u.__dict__
            u.pop('_sa_instance_state')
            a.append(u)
        msg['data'] = a;msg['success'] = 1;msg['code'] = 1001
        return jsonify(msg)  
@app.route('/mynote/notes',methods=['PUT','GET','DELETE','POST'])
def notes_page():
    msg = {'success':0,'data':{},'code':0,'detail':{}}
    auth = checkauth()
    if auth[0] == 0:
        status_code = 403
        msg['data'] = auth[1]
        response = make_response(json.dumps(msg), status_code)
        response.headers["Content-Type"] = "application/json"
        return response
    else: 
        userinfo = auth[1]
    if request.method == 'POST':
        data = request.get_data()
        json_data = json.loads(data.decode("utf-8"))
        content = json_data.get('content')
        query_key = json_data.get('query_key')
        tags = json_data.get('tags')
        front = False
        if json_data.get('front') == '1':
            front = True
        alert = False
        alert_time = 0
        if json_data.get('alert') == '1':
            alert = True
            alert_time = json_data.get('alert_time')
        uid = hashlib.md5(bytes(str(random.random()+time.time()).encode(encoding='utf-8'))).hexdigest()
        note = Notes(userinfo['id'],content,query_key,tags,uid,front,alert,alert_time)
        try:
            db.session.add(note)
            db.session.commit()
            msg['success'] =1;msg['data'] ='提交成功';msg['code'] =1001;msg['detail'] = Notes.query.filter(Notes.user_id==userinfo['id']).filter(Notes.uid==uid).first().id
        except Exception as e:
            db.session.rollback()
            msg['data'] ='失败';msg['code'] = 6;msg['detail'] = repr(e)
        return jsonify(msg)
    elif request.method == 'DELETE':
        id = request.values.get('id')
        note = Notes.query.filter(Notes.user_id==userinfo['id']).filter(Notes.id==id).first()
        try:
            db.session.delete(note)
            db.session.commit()
            msg['success'] = 1;msg['code'] = 1001;msg['data'] = '删除成功'
        except Exception as e:
            db.session.rollback()
            print(e)
            msg['detail'] = repr(e);msg['code'] = 7;msg['data'] = '失败'
        return jsonify(msg)
    elif request.method == 'GET':
        page = 1
        if request.values.get('p'):#是否指定第几页
            page = int(request.values.get('p'))
        if request.values.get('f'):#带了f参数则返回带了front tag的Notes
            info = Notes.query.filter(Notes.front==True).filter(Notes.user_id==userinfo['id']).order_by(Notes.create_time.desc()).paginate(page, per_page=10, error_out = False)
            a = []
            for u in info.items:
                u = u.__dict__
                u.pop('_sa_instance_state')
                a.append(u)
            return jsonify(a) 
        query_value = request.values.get('q')#带了q参数则执行模糊查找 
        if query_value != None:
        #模糊查找
            q_obj = request.values.get('o')
            info = Notes.query.filter(Notes.user_id==userinfo['id']).filter(Notes.query_key.like('%'+q_obj+'%')).all()
            a = []
            for u in info:
                u = u.__dict__
                u.pop('_sa_instance_state')
                a.append(u)
            return jsonify(a) 
        else:
            info = Notes.query.filter(Notes.user_id==userinfo['id']).order_by(Notes.create_time.desc()).paginate(page, per_page=10, error_out = False)
            a = []
            for u in info.items:
                u = u.__dict__
                u.pop('_sa_instance_state')
                a.append(u)
            return jsonify(a) 
    elif request.method == 'PUT':
        data = request.get_data()
        json_data = json.loads(data.decode("utf-8"))
        content = json_data.get('content')
        query_key = json_data.get('query_key')
        tags = json_data.get('tags')
        front = False
        if json_data.get('front') == '1':
            front = True
        alert = False
        alert_time = 0
        if json_data.get('alert') == '1':
            alert = True
            alert_time = json_data.get('alert_time')
        upd_id = json_data.get('updateId')
        Notes.query.filter(Notes.user_id==userinfo['id']).filter(Notes.id==upd_id).update({'content':content,\
            'query_key':query_key,'tags':tags,'front':front,'alert':alert,'alert_time':alert_time})
        try:
            db.session.commit()
            msg['success'] = 1;msg['data'] = '更新成功';msg['code'] = 1001
        except Exception as e:
            print(e)
            msg['data'] = '失败：'+repr(e);msg['code'] = 8
        return jsonify(msg)

@app.route('/mynote/access',methods=['POST'])#login, returns token.
def access():
    msg = {'success':0,'data':{},'code':0}
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    email = json_data.get('email')
    password_hash = json_data.get('password_hash')
    userinfo = Users.query.filter(Users.email==email).first()
    if userinfo == None:
        msg['data'] = '用户不存在';msg['code'] = 1
    elif userinfo.password_hash != password_hash:
        msg['data'] = '用户名或密码错误';msg['code'] = 2
    else:
        info = {'id':userinfo.id,'email':userinfo.email,'log_time':str(int(time.time())),'username':userinfo.username}
        res = tjwss.dumps(info)
        token = res.decode() 
        msg['data']['access_token'] = token; msg['success'] = 1;msg['code'] = 1002
    return jsonify(msg)
        
        
if __name__ == '__main__':
    #db.drop_all()
    db.create_all()
    app.run(host='0.0.0.0', debug=True ,port=6060)  