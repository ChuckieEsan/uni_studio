import time
import os
class LiveLog():
    t = time.time()
    def __init__(self) -> None:
        self.t = time.time()
        self.fd = open(os.path.join(os.getcwd(),'log','uwsgi.log'))
        self.fd.seek(0,2)
    
    def read(self)->str:
        s = ""
        lines = self.fd.readlines()
        for line in lines:
            if "GET /console/livelog" not in line:
                s+= (line+"<br>")
        return s