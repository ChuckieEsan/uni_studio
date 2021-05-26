import os
from hashlib import sha256
def cos_put(file):
    #file是个request.file中的一个文件，
    # 往common/static/cos里写文件，
    # 如果是image则顺便保存thumbnail
    # 返回文件的sha256作为fileid.
    file_suffix = file.filename.split('.')[-1].lower()
    fhash = sha256(file.read()).hexdigest()
    fpath = os.getcwd()+'/studio/apps/common/static/cos/{}.{}'
    fname = "{}.{}".format(fhash,file_suffix)
    file.seek(0)
    file.save(fpath.format(fhash,file_suffix))
    return fhash,fname