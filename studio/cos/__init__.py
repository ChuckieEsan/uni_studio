import os
from hashlib import sha256
from flask import url_for
from PIL import Image
def cos_put(file):
    #file是个request.file中的一个文件，
    # 往common/static/cos里写文件，
    # 如果是image则顺便保存thumbnail
    # 返回文件的sha256作为fileid.
    image_suffix = ['jpg','jpeg','png']
    file_suffix = file.filename.split('.')[-1].lower()
    fhash = sha256(file.read()).hexdigest()
    fpath = os.getcwd()+'/studio/apps/common/static/cos/{}.{}'
    fname = "{}.{}".format(fhash,file_suffix)
    file.seek(0)
    file.save(fpath.format(fhash,file_suffix))
    if file_suffix in image_suffix:
        file.seek(0)
        img = Image.open(fpath.format(fhash,file_suffix))
        isize = img.size
        newsize = (300,int(300*isize[1]/isize[0]))
        img.thumbnail(newsize)
        img.save(fpath.format("thumbnails/"+fhash,file_suffix))
    return fhash,fname

def url_for_cos(fname):
    return url_for('common.static',filename=os.path.join('cos',fname))