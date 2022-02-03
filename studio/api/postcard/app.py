# coding: utf-8
from __future__ import division
from flask import Flask, request, render_template, redirect, url_for, jsonify, make_response, send_file, session, Response, Blueprint, current_app
import datetime
import time
import os
import copy
import requests
import json
import hashlib
from shutil import copyfile
from PIL import Image
from requests_toolbelt import MultipartEncoder
from studio.models import db
from studio.models import PostcardCards as Cards
from studio.models import PostcardRoles as Roles
from studio.models import PostcardTemplates as Templates
from studio.models import PostcardUsers as Users

postcard = Blueprint('postcard', __name__, template_folder='templates', url_prefix='/postcard')
sizes = ['small', 'large']
APPID = os.environ.get('POSTCARD_APPID')
APPSECRET = os.environ.get('POSTCARD_APPSECRET')

if not APPID or not APPSECRET:
    try:
        current_app.logger.error('no appid or appsecret in env')
        exit(-11)
    except:
        pass


def md5(arg):
    m = hashlib.md5()
    b = arg.encode(encoding='utf-8')
    m.update(b)
    return m.hexdigest()


def do_return(code, msg):
    status_code = code
    response = make_response(msg, status_code)
    return response


def process_sqlalchemy_arr(arr):
    result = []
    for item in arr:
        item = item.__dict__
        item.pop('_sa_instance_state')
        result.append(item)
    return result


@postcard.route('/upload', methods=['POST', 'GET'])
def uploader():
    msg = {'success': 0, 'exist': 0, 'data': 'unknown error', 'errorCode': 0}
    wxid = request.headers.get('openid')
    if not wxid:
        msg['errorCode'] = 1
        msg['data'] = 'WXID MISSING'
        return jsonify(msg)
    _file = request.files.get('file')
    file_suffix = _file.filename.split('.')[-1]
    if file_suffix not in ['png', 'PNG', 'jpg', 'JPG', 'JPEG', 'jpeg', 'mp3']:
        msg['errorCode'] = 2
        msg['data'] = 'bad suffix'
        return jsonify(msg)
    path = os.getcwd() + '/data/postcard/static/upload/' + wxid + '/temp'
    if not os.path.exists(path):
        os.makedirs(path)
    if file_suffix in ['png', 'PNG', 'jpg', 'JPG', 'JPEG', 'jpeg']:
        try:
            _file.save(path + '/image.png')
            msg['success'] = 1
            msg['data'] = '图片上传成功'
        except Exception as e:
            msg['data'] = repr(e)
    else:
        try:
            _file.save(path + '/audio.mp3')
            msg['success'] = 1
            msg['data'] = '音频上传成功'
        except Exception as e:
            msg['data'] = repr(e)
    return jsonify(msg)


@postcard.route('/<op_type>/<id>', methods=['GET', 'POST'])
def resource_handler(op_type, id):
    if request.method == 'GET':
        if op_type == 'image':
            size = request.values.get('size')  # 有small跟large
            if size not in sizes:
                size = 'small'
            this_card = Cards.query.filter(Cards.id == id).first()
            if this_card:
                try:
                    return send_file(os.getcwd() + '/data/postcard/static/upload/' + this_card.wx_openid + '/' +
                                     this_card.dir_name + '/' + size + '.png')
                except Exception as e:
                    return do_return(500, repr(e))
            else:
                return do_return(404, 'not found')
        elif op_type == 'audio':
            this_card = Cards.query.filter(Cards.id == id).first()
            if this_card.with_audio == 0:
                try:
                    response = send_file(os.getcwd() + '/data/postcard/static/upload/' + this_card.wx_openid + '/' +
                                         this_card.dir_name + '/' + 'audio.mp3')
                    response.headers["Content-Type"] = 'audio/mp3'
                    return response
                except Exception as e:
                    return do_return(500, repr(e))
            else:
                return do_return(404, 'not found---')
        elif op_type == 'template':
            this_template = Templates.query.filter(Templates.id == id).first()
            if this_template:
                target = request.values.get('target')
                size = request.values.get('size')  # 有small跟large
                if size not in sizes:
                    size = 'small'
                if target == 'image':
                    try:
                        return send_file(os.getcwd() + '/data/postcard/static/templates/' + str(id) + '/' + size +
                                         '.png')
                    except Exception as e:
                        return do_return(500, repr(e))
                elif target == 'audio':
                    if this_template.with_audio:
                        try:
                            return send_file(os.getcwd() + '/data/postcard/static/templates/' + str(id) + '/audio.mp3')
                        except Exception as e:
                            return do_return(500, repr(e))
                    else:
                        return do_return(404, 'no audio')
                else:
                    return do_return(404, 'no resource')
            else:
                return do_return(404, 'not found')
        elif op_type == 'roles':
            roles = Roles.query.filter(Roles.id != 1).all()
            roles = process_sqlalchemy_arr(roles)
            return jsonify(roles)
        else:
            return do_return(404, 'not found')
    else:
        return do_return(500, 'not ready')


@postcard.route('/card', methods=['GET', 'POST', 'PUT', 'DELETE'])
def card_handler():
    msg = {'success': 0, 'data': {}, 'errorCode': 0}
    if request.method == 'POST':
        data = request.get_data()
        if request.headers.get('openid') and Users.query.filter(Users.wxid == request.headers.get('openid')).first():
            try:
                json_data = json.loads(data.decode("utf-8"))  # 是dict
                wx_openid = json_data.get('wx_openid')
                title = json_data.get('title')
                description = json_data.get('description')
                content = json_data.get('content')
                with_audio = int(json_data.get('with_audio'))
                with_img = int(json_data.get('with_img'))
                crop = json_data.get('crop')
                display = json_data.get('display')
                dir_name = str(int(time.time())) + '-' + md5(wx_openid + md5(str(time.time()) + content))[9:26]
                new_card = Cards(wx_openid,
                                 title,
                                 description,
                                 content,
                                 with_audio=with_audio,
                                 with_img=with_img,
                                 crop=crop,
                                 display=display,
                                 dir_name=dir_name)
                try:
                    db.session.add(new_card)
                    db.session.commit()
                    try:
                        path = os.getcwd() + '/data/postcard/static/upload/' + wx_openid + '/' + dir_name
                        if not os.path.exists(path):
                            os.makedirs(path)

                        if with_img == 0:
                            if os.path.exists(os.getcwd() + '/data/postcard/static/upload/' + wx_openid +
                                              '/temp/image.png'):
                                copyfile(os.getcwd() + '/data/postcard/static/upload/' + wx_openid + '/temp/image.png',
                                         path + '/large.png')
                                img = Image.open(path + '/large.png')
                                width = int(img.size[0])
                                height = int(img.size[1])
                                if width > 400:
                                    scale = 400 / width
                                    new_w = int(width * scale)
                                    new_h = int(height * scale)
                                    img = img.resize((new_w, new_h), Image.ANTIALIAS)
                                img.save(path + '/small.png')

                        if with_audio == 0:
                            if os.path.exists(os.getcwd() + '/data/postcard/static/upload/' + wx_openid +
                                              '/temp/audio.mp3'):
                                copyfile(os.getcwd() + '/data/postcard/static/upload/' + wx_openid + '/temp/audio.mp3',
                                         path + '/audio.mp3')

                        new_id = Cards.query.filter(Cards.dir_name == dir_name).first().id
                        msg['success'] = 1
                        msg['data'] = '新建成功'
                        msg['id'] = new_id
                    except Exception as e:
                        msg['data'] = repr(e)
                        msg['errorCode'] = 5
                except Exception as e:
                    db.session.rollback()
                    msg['data'] = repr(e)
                    msg['errorCode'] = 3
            except Exception as e:
                msg['data'] = repr(e)
                msg['errorCode'] = 4
        else:
            return do_return(403, 'unauthorized')
    elif request.method == 'GET':
        if request.values.get('id') and request.values.get('id').isdigit():
            id = int(request.values.get('id'))
            this_card = Cards.query.filter(Cards.id == id).first()
            if this_card:
                this_card = this_card.__dict__
                this_card.pop('_sa_instance_state')
                msg['data'] = this_card
                msg['success'] = 1
                msg['data']['is_liked'] = False
                if request.headers.get('openid'):
                    this_user = Users.query.filter(Users.wxid == request.headers.get('openid')).first()
                    if this_user:
                        msg['data']['is_liked'] = this_user.id in json.loads(this_card['liked_by'])
            else:
                msg['data'] = 'not found'
                msg['errorCode'] = 10
        else:
            msg['data'] = 'invalid id'
            msg['errorCode'] = 11
    elif request.method == 'PUT':
        data = request.get_data()
        if request.headers.get('openid'):
            this_user = Users.query.filter(Users.wxid == request.headers.get('openid')).first()
            if this_user:
                try:
                    json_data = json.loads(data.decode("utf-8"))  # 是dict
                    if json_data.get('id'):
                        if json_data.get('likes'):
                            op_val = str(json_data['likes'])
                            this_card = Cards.query.filter(Cards.id == json_data.get('id'))
                            _card = this_card.first()
                            if op_val == '1':
                                op_num = 1
                                if this_user.id not in json.loads(_card.liked_by):
                                    result_likes = _card.likes + op_num
                                    result_liked_by = json.loads(_card.liked_by)
                                    result_liked_by.append(this_user.id)
                                    this_card.update({'likes': result_likes, 'liked_by': json.dumps(result_liked_by)})
                                    try:
                                        db.session.commit()
                                        msg['data'] = '点赞成功'
                                        msg['success'] = 1
                                    except Exception as e:
                                        db.session.rollback()
                                        msg['data'] = repr(e)
                                        msg['errorCode'] = 18
                                else:
                                    msg['data'] = '只能点赞一次'
                                    msg['errorCode'] = 23
                            elif op_val == '-1':
                                op_num = -1
                                result_likes = _card.likes + op_num
                                result_liked_by = json.loads(_card.liked_by)
                                if this_user.id in result_liked_by:
                                    result_liked_by.remove(this_user.id)
                                    this_card.update({'likes': result_likes, 'liked_by': json.dumps(result_liked_by)})
                                    try:
                                        db.session.commit()
                                        msg['data'] = '取消点赞成功'
                                        msg['success'] = 1
                                    except Exception as e:
                                        db.session.rollback()
                                        msg['data'] = repr(e)
                                        msg['errorCode'] = 18
                                else:
                                    msg['data'] = '未点赞，不能取消'
                                    msg['errorCode'] = 29
                            else:
                                msg['data'] = 'invalid operand'
                                msg['errorCode'] = 28
                        else:
                            this_card = Cards.query.filter(Cards.id == json_data.get('id'))  # 完整更新，预留的接口，不一定好用
                            try:
                                this_card.update(json_data)
                                db.session.commit()
                            except Exception as e:
                                db.session.rollback()
                                msg['data'] = repr(e)
                                msg['errorCode'] = 24
                    else:
                        msg['data'] = 'params missing'
                        msg['errorCode'] = 19
                except Exception as e:
                    msg['data'] = repr(e)
                    msg['errorCode'] = 20
            else:
                msg['data'] = 'unauthorized'
                msg['errorCode'] = 22
        else:
            msg['data'] = 'unauthorized'
            msg['errorCode'] = 21
    elif request.method == 'DELETE':
        if request.headers.get('openid'):
            this_user = Users.query.filter(Users.wxid == request.headers.get('openid')).first()
            if this_user:
                id = request.values.get('id')
                this_card = Cards.query.filter(Cards.id == id).first()
                if this_card and str(this_card.wx_openid) == str(this_user.wxid):
                    try:
                        db.session.delete(this_card)
                        db.session.commit()
                        msg['data'] = '删除成功'
                        msg['success'] = 1
                    except Exception as e:
                        msg['data'] = repr(e)
                        msg['errorCode'] = 27
            else:
                msg['data'] = 'unauthorized'
                msg['errorCode'] = 25
        else:
            msg['data'] = 'unauthorized'
            msg['errorCode'] = 25
    return jsonify(msg)


@postcard.route('/code', methods=['GET', 'POST'])
def pcode():
    msg = {'success': 0, 'data': {}, 'errorCode': 0, 'new': 0}
    if request.method == 'GET':
        if request.headers.get('openid') and Users.query.filter(
                Users.wxid == request.headers.get('openid')).first() and request.values.get('id'):
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&'
            params = 'appid=' + APPID + '&secret=' + APPSECRET
            try:
                r = requests.get(url + params)
                result = json.loads(r.text)
                err_code = result.get('errcode')
                err_msg = result.get('errmsg')
                access_token = result.get('access_token')
                expires_in = result.get('expires_in')
                id = request.values.get('id')
                if id.isdigit():
                    id = int(id)
                else:
                    id = 0
                if not err_code:
                    r2 = requests.post('https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=' + access_token,
                                       data=json.dumps({'scene': str('id=' + str(id))}),
                                       headers={"Accept": "text/html,image/jpg,*/*;q=0.8"})
                    if len(r2.text) > 100:
                        try:
                            with open(os.getcwd() + '/data/postcard/static/qr/' + str(id) + '.jpg', "wb") as f:
                                f.write(r2.content)
                            msg['data'] = 'https://www.dutbit.com/postcard/static/qr/' + str(id) + '.jpg'
                            msg['success'] = 1
                        except Exception as e:
                            msg['data'] = repr(e)
                            msg['errorCode'] = 29
                    else:
                        result2 = json.loads(r2.text)
                        err_code = result2.get('errcode')
                        msg['data'] = result2.get('errmsg')
                        msg['errorCode'] = err_code
                else:
                    msg['data'] = err_msg
                    msg['errorCode'] = err_code
            except Exception as e:
                msg['data'] = repr(e)
                msg['errorCode'] = 16
        else:
            msg['errorCode'] = 17
            msg['data'] = 'unauthorized'
        return jsonify(msg)
    data = request.get_data()
    last_ip = request.remote_addr
    try:
        json_data = json.loads(data.decode("utf-8"))
        code = json_data.get('code')
        avt_url = json_data.get('avt_url')
        wx_name = json_data.get('wx_name')
        params = '?appid=' + APPID + '&secret=' + APPSECRET + '&js_code=' + code + '&grant_type=authorization_code'
        url = 'https://api.weixin.qq.com/sns/jscode2session' + params
        try:
            r = requests.get(url)
            result = json.loads(r.text)
            err_code = result.get('errcode')
            err_msg = result.get('errmsg')
            wx_openid = result.get('openid')
            if err_code == None:  # 请求json2code正常的时候返回的err_code 是空   这里会报错
                if Users.query.filter(Users.wxid == wx_openid).first() == None:
                    new_user = Users(wx_openid, last_ip, role_id=2, wx_name=wx_name, avt_url=avt_url)
                    try:
                        db.session.add(new_user)
                        db.session.commit()
                        msg['new'] = 1
                        msg['data'] = {'openid': wx_openid}
                        msg['success'] = 1
                    except Exception as e:
                        msg['data'] = repr(e)
                        msg['errorCode'] = 8
                else:
                    msg['data'] = {'openid': wx_openid}
                    msg['success'] = 1
            else:
                msg['data'] = err_msg
                msg['errorCode'] = err_code
        except Exception as e:
            msg['data'] = repr(e)
            msg['errorCode'] = 6
    except Exception as e:
        msg['data'] = repr(e)
        msg['errorCode'] = 7
    return jsonify(msg)


@postcard.route('/public', methods=['GET'])
def public_handler():
    msg = {'success': 0, 'data': {}, 'errorCode': 0}
    c = []
    if not request.values.get('sort') and request.values.get('sort') != 'likes':
        card_list = Cards.query.filter(Cards.display == True).order_by(Cards.create_time.desc()).all()
    else:
        card_list = Cards.query.filter(Cards.display == True).order_by(Cards.likes.desc()).all()
    base_role_query = Roles.query
    if request.headers.get('openid'):
        this_visitor = Users.query.filter(Users.wxid == request.headers.get('openid')).first()
        if this_visitor:
            this_visitor_id = this_visitor.id
        else:
            this_visitor_id = None
    else:
        this_visitor_id = None
    for card in card_list:
        card = card.__dict__
        card.pop('_sa_instance_state')
        card_creator = Users.query.filter(Users.wxid == card['wx_openid']).first()
        card['is_liked'] = this_visitor_id in json.loads(card['liked_by'])
        if card_creator:
            card['role_id'] = card_creator.role_id
            card['role_name'] = base_role_query.filter(Roles.id == card['role_id']).first().name
            card['avt_url'] = card_creator.avt_url
            card['wx_name'] = card_creator.wx_name
        else:
            card['role_id'] = None
            card['avt_url'] = None
            card['wx_name'] = None
            card['role_name'] = None
        c.append(card)
    msg['data'] = c
    msg['success'] = 1
    msg['logged_in'] = this_visitor_id != None
    return jsonify(msg)


@postcard.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_handler():
    msg = {'success': 0, 'data': {}, 'errorCode': 0}
    if request.headers.get('openid') and Users.query.filter(Users.wxid == request.headers.get('openid')).first():
        this_user = Users.query.filter(Users.wxid == request.headers.get('openid')).first()
        if request.method == 'GET':
            user_cards = process_sqlalchemy_arr(
                Cards.query.filter(Cards.wx_openid == request.headers.get('openid')).order_by(
                    Cards.create_time.desc()).all())
            user_saves = json.loads(this_user.cards_saved)
            user_saves_list = process_sqlalchemy_arr(Cards.query.filter(Cards.id.in_(user_saves)).all())
            msg['data'] = {'user_cards': user_cards, 'user_saves': user_saves_list, 'role': this_user.role_id}
            msg['success'] = 1
            return jsonify(msg)
        elif request.method == 'PUT':
            data = request.get_data()
            try:
                json_data = json.loads(data)
                new_save = json_data.get('save')
            except Exception as e:
                msg['data'] = repr(e)
                msg['errorCode'] = 33
                return jsonify(msg)
            if new_save and json_data.get('id'):
                if Cards.query.filter(Cards.id == json_data.get('id')):
                    base_user_query = Users.query.filter(Users.wxid == request.headers.get('openid'))
                    old_card_list = json.loads(base_user_query.first().cards_saved)
                    if str(new_save) == '1' and json_data.get('id') not in old_card_list:
                        old_card_list.append(json_data.get('id'))
                        base_user_query.update({'cards_saved': json.dumps(old_card_list)})
                        try:
                            db.session.commit()
                            msg['success'] = 1
                            msg['data'] = '收藏成功'
                        except Exception as e:
                            msg['data'] = repr(e)
                            msg['errorCode'] = 31
                    elif str(new_save) == '-1' and json_data.get('id') in old_card_list:
                        old_card_list.remove(json_data.get('id'))
                        base_user_query.update({'cards_saved': json.dumps(old_card_list)})
                        try:
                            db.session.commit()
                            msg['success'] = 1
                            msg['data'] = '取消成功'
                        except Exception as e:
                            msg['data'] = repr(e)
                            msg['errorCode'] = 32
                    else:
                        msg['data'] = 'operand error'
                        msg['errorCode'] = 30
                else:
                    msg['data'] = 'operand error'
                    msg['errorCode'] = 34
            else:
                msg['data'] = 'operand error'
                msg['errorCode'] = 35
            new_role_id = json_data.get('role_id')
            if new_role_id and str(new_role_id).isdigit() and Roles.query.filter(Roles.id == new_role_id).first():
                Users.query.filter(Users.wxid == request.headers.get('openid')).update({'role_id': new_role_id})
                try:
                    db.session.commit()
                    msg['success'] = 1
                    msg['data'] = '更新成功'
                except Exception as e:
                    db.session.rollback()
                    msg['data'] = repr(e)
                    msg['errorCode'] = 15
            return jsonify(msg)
    else:
        return do_return(403, 'unauthorized')


@postcard.route('/templates', methods=['GET', 'POST'])  # 拿list
def template_handler():
    msg = {'success': 0, 'data': {}, 'errorCode': 0}
    if request.method == 'GET':
        templates = Templates.query.all()
        templates = process_sqlalchemy_arr(templates)
        msg['success'] = 1
        msg['data'] = templates
    elif request.method == 'POST':
        return do_return(500, '1')
    return jsonify(msg)


@postcard.route('/home', methods=['GET', 'POST'])
def homepage():
    return render_template('upload.html')


if __name__ == '__main__':
    # a#pp.run(host='0.0.0.0', debug=True ,port=6060)
    pass
