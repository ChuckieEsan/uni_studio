from flask import Blueprint, Response, send_file, jsonify, g,  request, current_app
from flask_cors import CORS
from studio.models import db, UserUsers
from pathlib import Path

MUST_LOGIN_PATH = ['/console', '/chat']

apivue = Blueprint("apivue", __name__, static_folder='static')
CORS(apivue)

pthDayImage = Path.cwd().joinpath('data/dayImage')
ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif']


@apivue.before_request
def interceptor():
    try:
        token = request.cookies['token']
        data = current_app.tjwss.loads(token)
        user = UserUsers.query.filter(UserUsers.id == data['id']).first()
        g.user = user
        current_app.logger.info("user=", g.user.id)
    except Exception as e:
        g.user = None

    for p in MUST_LOGIN_PATH:
        if request.path.startswith('/apivue'+p) and not g.user:
            return jsonify({"success": False, "details": "需要登录"})


@apivue.route('/login', methods=['POST'])
def users_login():
    data = request.get_json()
    user = UserUsers.query.filter(UserUsers.email == str(data.get('email')).strip())\
        .filter(UserUsers.password == str(data.get('password')).strip()).first()
    if user:
        info = {'id': user.id}
        token = current_app.tjwss.dumps(info).decode()
        resp: Response = jsonify({"success": True, 'token': token})
        return resp
    return jsonify({"success": False, "details": "用户名或密码错误"})


@apivue.route('/day-image/cata')
def dayImage_cata():
    lstCata = [str(x.name) for x in pthDayImage.iterdir() if x.is_dir()]
    lstCata = [x for x in lstCata if not x.endswith("deleted")]
    return jsonify({"lstCata": lstCata})


@apivue.route('/day-image/cont/<dirCont>')
def dayImage_cont(dirCont):
    pthDir = pthDayImage.joinpath(dirCont)
    lstCont = [str(x.name) for x in pthDir.iterdir() if x.is_file()]
    return jsonify({"lstCont": lstCont})


@apivue.route('/day-image/new-dir/<nameDir_new>')
def dayImage_newDir(nameDir_new):
    try:
        pthDayImage.joinpath(nameDir_new).mkdir()
        return '已创建文件夹'
    except FileExistsError:
        return '文件夹已存在', 404


@apivue.route('/day-image/del-dir/<nameDir>')
def dayImage_delDir(nameDir):
    pthDir = pthDayImage.joinpath(nameDir)
    pthDir_new = pthDir.with_name(nameDir+'_deleted')
    pthDir.rename(pthDir_new)
    return '已删除文件夹'


@apivue.route('/day-image/rename-dir', methods=['POST'])
def dayImage_renameDir():
    pthDir = pthDayImage.joinpath(request.json['nameDir_old'])
    pthDir_new = pthDir.with_name(request.json['nameDir_new'])
    pthDir.rename(pthDir_new)
    return '已重命名文件夹'


@apivue.route('/day-image/img/<path:dfnImg>')
def dayImage_img(dfnImg):
    pthImg = pthDayImage.joinpath(dfnImg)
    return send_file(str(pthImg))


@apivue.route('/day-image/upload/<dirCont>', methods=['POST'])
def dayImage_upload(dirCont):
    if 'file' not in request.files:
        return 'No file part'
    fileImg = request.files['file']
    if fileImg.filename == '':
        return 'No selected file'
    pthImg = pthDayImage.joinpath(dirCont, Path(fileImg.filename).name)
    if pthImg.suffix in ALLOWED_EXTENSIONS:
        fileImg.save(pthImg)
        return 'ok'
    else:
        return 'not alllowed'


@apivue.route('/day-image/delete/<path:dfnImg>')
def dayImage_delete(dfnImg):
    try:
        pthDayImage.joinpath(dfnImg).unlink()
        return '已删除'
    except FileNotFoundError:
        return '文件不存在', 404
