from studio.issues import issues
from flask import url_for,redirect,render_template,request,flash

@issues.route('/',methods=['GET','POST'])
def root():
    if request.method=='GET':
        flash("test")
        return render_template(
            "issues_index.html",
            referer=request.referrer
        )