import os
def join_upload_dir(s:str)->str:
    return os.path.join(os.getcwd(),'studio/apps/fileservice/',s)