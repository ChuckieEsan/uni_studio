from studio.issues import issues
from flask import url_for, redirect, render_template, request, jsonify,g
from studio.models import db, IssuesIssues, IssueTypes
from studio.interceptors import roles_required,session_required

@issues.route('/data/<int:page_id>')
@session_required('/issues')
@roles_required(['vol_time_admin','super_admin'])
def get_issues(page_id=1):
    role = '志愿时长查询管理员'
    vt = False#i dont know what this is for
    current_page = page_id
    per_page = 15 if request.values.get('per_page') is None else int(request.values.get('per_page'))
    issues = IssuesIssues.query\
        .filter(IssuesIssues.status == 'pending')\
        .order_by(IssuesIssues.created_at.desc())#\
        #.paginate(current_page, per_page=per_page, error_out=False)
        #.items
    a = []
    for u in issues:#.items:
        u = u.__dict__
        u.pop('_sa_instance_state')
        a.append(u)
    return jsonify(a) 
    #return jsonify(issues)
@issues.route('/manage/')
@session_required('/issues')
@roles_required(['vol_time_admin','super_admin'])
def manage_home():
    role = g.role
    max_page = db.session.query(IssuesIssues).count()
    per_page = 10
    pages = range(1,int(max_page/per_page)+2)
    issuetypes = IssueTypes.query.all()
    return render_template(
        'issues_manage.html',
        role=role,
        issuetypes=issuetypes,
        pages=pages
    )

@issues.route('/manage/types', methods=['POST'])
@session_required('/issues')
@roles_required(['super_admin'])
def types():
    _t = IssueTypes(
            typename=request.form.get('name'),
            typevalue=request.form.get('value'),
            created_by=g._id
        )
    try:
        db.session.add(_t)
        db.session.commit()
    except Exception as E:
        db.session.rollback()
        print(E)
    return redirect(request.referrer+'#modal')
