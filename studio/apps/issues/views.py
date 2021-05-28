from flask.globals import current_app
from studio.apps.issues import issues
from flask import url_for,redirect,render_template,request,flash
from studio.models import IssueTypes,IssuesIssues,db
@issues.route('/',methods=['GET','POST'])
def root():
    if request.method=='GET':
        timeout = bool(request.values.get('timeout'))
        referer = request.referrer if request.referrer is not None else ''
        issuetypes = IssueTypes.query.order_by(IssueTypes.priority.desc()).all()
        return render_template(
            "issues_index.html",
            referer=referer,
            timeout=timeout,
            issuetypes=issuetypes,
            title="反馈",
        )
    if request.method=='POST':
        print(current_app.hcaptcha.verify())
        _i = IssuesIssues(
            ip=request.remote_addr,
            url=request.form.get('url'),
            contact=request.form.get('contact'),
            type=request.form.get('type'),
            content=request.form.get('content'),
            user_id=None
        )
        db.session.add(_i)
        db.session.commit()
        flash('提交成功，感谢您的反馈')
        return redirect(url_for('issues.root',timeout=True))
