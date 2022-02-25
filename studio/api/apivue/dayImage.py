from flask import Blueprint, send_file, jsonify, request, jsonify
from pathlib import Path
from PIL import Image
import os

dayImage = Blueprint('dayImage', __name__, url_prefix='/day-image')

pthdayImage = Path(os.environ.get('DAY_IMAGE_FOLDER'))
ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif']


@dayImage.route('/cata')
def dayImage_cata():
    lstCata = [str(x.name) for x in pthdayImage.iterdir() if x.is_dir()]
    lstCata = [x for x in lstCata if not x.endswith("deleted")]
    return jsonify({"lstCata": lstCata})


@dayImage.route('/cont/<dirCont>')
def dayImage_cont(dirCont):
    pthDir = pthdayImage.joinpath(dirCont)
    lstCont = [str(x.name) for x in pthDir.iterdir() if x.is_file() and not x.stem.endswith("@full")]
    return jsonify({"lstCont": lstCont})


@dayImage.route('/new-dir/<nameDir_new>')
def dayImage_newDir(nameDir_new):
    try:
        pthdayImage.joinpath(nameDir_new).mkdir()
        return '已创建文件夹'
    except FileExistsError:
        return '文件夹已存在', 404


@dayImage.route('/del-dir/<nameDir>')
def dayImage_delDir(nameDir):
    pthDir = pthdayImage.joinpath(nameDir)
    pthDir_new = pthDir.with_name(nameDir + '_deleted')
    pthDir.rename(pthDir_new)
    return '已删除文件夹'


@dayImage.route('/rename-dir', methods=['POST'])
def dayImage_renameDir():
    pthDir = pthdayImage.joinpath(request.json['nameDir_old'])
    pthDir_new = pthDir.with_name(request.json['nameDir_new'])
    pthDir.rename(pthDir_new)
    return '已重命名文件夹'


@dayImage.route('/img/<path:dfnImg>')
def dayImage_img(dfnImg):
    pthImg = pthdayImage.joinpath(dfnImg)
    return send_file(str(pthImg))


@dayImage.route('/upload/<dirCont>', methods=['POST'])
def dayImage_upload(dirCont):
    if 'file' not in request.files:
        return 'No file part'
    fileImg = request.files['file']
    if fileImg.filename == '':
        return 'No selected file'
    filename = Path(fileImg.filename).name
    pthImg = pthdayImage.joinpath(dirCont, filename)
    if pthImg.suffix in ALLOWED_EXTENSIONS:
        fileImg.save(pthImg.with_name(f'{pthImg.stem}@full{pthImg.suffix}'))
        img = Image.open(fileImg)
        # img.save(pthImg.with_name(f'{pthImg.stem}@full.jpg'))
        width = 1080
        height = int(img.size[1]*width/img.size[0])
        img = img.resize((width, height))
        img.save(pthImg.with_suffix('.png'))
        return 'ok'
    else:
        return 'not alllowed'


@dayImage.route('/delete/<path:dfnImg>')
def dayImage_delete(dfnImg):
    try:
        pthdayImage.joinpath(dfnImg).unlink()
        return '已删除'
    except FileNotFoundError:
        return '文件不存在', 404
