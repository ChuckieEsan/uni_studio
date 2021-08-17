from studio.apps.console import console
from flask import url_for, redirect, render_template, request, jsonify, session, g
from studio.models import db, IssuesIssues, IssueTypes


@console.route('/issues/data')
def get_issues():
    pageNumber = int(request.values.get('pageNumber'))
    pageSize = 15 if request.values.get(
        'pageSize') is None else int(request.values.get('pageSize'))
    issues: list[IssuesIssues] = IssuesIssues.query.filter(IssuesIssues.status == 'pending')\
        .order_by(IssuesIssues.created_at.desc())\
        .paginate(pageNumber, per_page=pageSize, error_out=False).items
    issueList = []
    for issue in issues:  # .items:
        issue = issue.__dict__
        issue.pop('_sa_instance_state')
        issue['created_at'] = issue['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        issueList.append(issue)
    return jsonify({"total": db.session.query(IssuesIssues).count(), "rows": issueList})


@console.route('/issues')
def issues_root():
    issuetypes = IssueTypes.query.all()
    return render_template(
        'issues_manage.html',
        issuetypes=issuetypes,
        bootstrap_table=True,
        title='Issues'
    )


@console.route('/issues/types', methods=['POST'])
def issues_types_handler():
    priority = str(request.form.get('priority'))
    _t = IssueTypes(
        typename=request.form.get('name'),
        typevalue=request.form.get('value'),
        priority=int(priority) if priority.isdigit() else 1,
        duty_user=g.user.id,
        created_by=g.user.id
    )
    try:
        db.session.add(_t)
        db.session.commit()
    except Exception as E:
        db.session.rollback()
        print(E)
    return redirect(request.referrer+'#modal')
