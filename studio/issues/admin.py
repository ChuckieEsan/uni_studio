from studio.issues import issues
from flask import url_for,redirect,render_template,request

@issues.route('/manage')
def manage():
    return render_template('issues_manage.html')
