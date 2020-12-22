from studio.issues import issues
from flask import url_for,redirect,render_template,request,flash
from studio.models import IssueTypes,IssuesIssues,db
@issues.route('/',methods=['GET','POST'])
def root():
    if request.method=='GET':
        timeout = bool(request.values.get('timeout'))
        referer = request.referrer if request.referrer is not None else ''
        issuetypes = IssueTypes.query.all()
        return render_template(
            "issues_index.html",
            referer=referer,
            timeout=timeout,
            issuetypes=issuetypes,
            title="反馈"
        )
    if request.method=='POST':
        _i = IssuesIssues(
            ip=request.remote_addr,
            url=request.form.get('url'),
            contact=request.form.get('contact'),
            type=request.form.get('type'),
            content=request.form.get('content'),
            user_id=None
        )
        print('type:',request.form.get('type'))
        print('1:{}'.format(_i.id))
        db.session.add(_i)
        print('2:{}'.format(_i.id))
        try:
            db.session.commit()
            print('3:{}'.format(_i.id))
            flash('提交成功，感谢您的反馈')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('提交失败，请直接联系管理员')
        return redirect(url_for('issues.root',timeout=True))
