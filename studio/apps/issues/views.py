from flask.globals import current_app
from studio.apps.issues import issues
from flask import url_for, redirect, render_template, request, flash, g
from studio.models import IssueTypes, IssuesIssues, db, UserUsers
from studio.utils.send_chat import send_chat, start_chat
from studio.utils.send_mail import send_mail


@issues.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
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
    if request.method == 'POST':
        if not current_app.hcaptcha.verify():
            flash('验证码无效')
            return redirect(url_for('issues.root', timeout=True))
        issue = IssuesIssues(ip=request.remote_addr,
                             url=request.form.get('url'),
                             type=request.form.get('type'),
                             contact=request.form.get('contact'),
                             name=request.form.get('name'),
                             stu_id=request.form.get('stu_id'),
                             content=request.form.get('content'),
                             user_id=None if not g.user else g.user.id)
        db.session.add(issue)
        db.session.commit()
        issueType = IssueTypes.query.filter(IssueTypes.typevalue == request.form.get('type')).first()

        to = UserUsers.query.filter(UserUsers.id == issueType.duty_user).first().email
        try:
            send_mail(to=to, content=str(issue), subject='dutbit.com 新增反馈通知', type='plain')
            flash('发送成功')
        except Exception as e:
            flash(e)

        if g.user:
            to = UserUsers.query.filter(UserUsers.role_bits.op('&')(1) == 1).first()
            head = start_chat(g.user.id, to.id, first_alias=g.user.email, second_alias='反馈处理')
            send_chat(from_id=g.user.id, text='查看反馈工单{}'.format(issue.id), to_id=to.id, head=head)
        flash('提交成功，感谢您的反馈')
        return redirect(url_for('issues.root', timeout=True))
