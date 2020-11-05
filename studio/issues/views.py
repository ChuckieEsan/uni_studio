from studio.issues import issues
from flask import url_for,redirect,render_template,request

@issues.route('/',methods=['GET','POST'])
def root():
    if request.method=='GET':
        return render_template(
            "issues_index.html",
            referer=request.referrer
        )