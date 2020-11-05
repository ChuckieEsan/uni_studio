from studio.issues import issues
from flask import url_for, redirect, render_template, request
from studio.models import db, IssuesIssues


@issues.route('/manage/<int:page_id>')
def manage(page_id=1):
    role = '志愿时长查询管理员'
    vt = False
    current_page = page_id 
    issues = IssuesIssues.query.filter(IssuesIssues.status == 'pending').\
        order_by(IssuesIssues.created_at.desc()).paginate(
            current_page, per_page=10, error_out=False).items

    return render_template(
        'issues_manage.html',
        role=role,
        issues=issues
    )
