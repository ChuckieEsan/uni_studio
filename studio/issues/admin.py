from studio.issues import issues
from flask import url_for, redirect, render_template, request
from studio.models import db, IssuesIssues, IssueTypes


@issues.route('/manage/<int:page_id>')
def manage(page_id=1):
    role = '志愿时长查询管理员'
    vt = False#i dont know what this is for
    current_page = page_id
    issues = IssuesIssues.query\
        .filter(IssuesIssues.status == 'pending')\
        .paginate(current_page, per_page=10, error_out=False)\
        .items
    max_page = db.session.query(IssuesIssues).count()
    per_page = 10
    pages = [1]
    pages = range(1,int(max_page/per_page)+2)
    issuetypes = IssueTypes.query.all()
    return render_template(
        'issues_manage.html',
        role=role,
        issues=issues,
        issuetypes=issuetypes,
        pages=pages
    )
@issues.route('/manage/')
def manage_home():
    role = '志愿时长查询管理员'
    max_page = db.session.query(IssuesIssues).count()
    per_page = 10
    pages = [1]
    pages = range(1,int(max_page/per_page)+2)
    issuetypes = IssueTypes.query.all()
    return render_template(
        'issues_manage.html',
        role=role,
        issuetypes=issuetypes,
        pages=pages
    )

@issues.route('/manage/types', methods=['GET', 'POST'])
def types():
    if request.method == 'GET':
        types = IssueTypes.query.all()
        print(types)
        return render_template(
            'issues_types_manage.html',
            types=types
        )
    if request.method == 'POST':
        _t = IssueTypes(
            typename=request.form.get('name'),
            typevalue=request.form.get('value'),
            created_by='tzy15368'
        )
        try:
            db.session.add(_t)
            db.session.commit()
        except Exception as E:
            db.session.rollback()
            print(E)
        return redirect(request.referrer+'#modal')
