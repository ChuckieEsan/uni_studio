from .init import console
from flask import url_for, redirect, render_template, request, jsonify, session, g, current_app
from studio.models import db, IssuesIssues, IssueTypes


@console.route('/issues')
def issues_root():
    issuetypes = IssueTypes.query.all()
    return render_template(
        'issues_manage.html',
        issuetypes=issuetypes,
        bootstrap_table=True,
        title='Issues'
    )


@console.route('/issues/data')
def get_issues():
    pageNumber = int(request.values.get('pageNumber'))
    pageSize = 15 if request.values.get(
        'pageSize') is None else int(request.values.get('pageSize'))
    searchText: str = request.values.get('searchText')

    if searchText.isdigit():
        issuesQuery = db.session.query(IssuesIssues).filter(
            IssuesIssues.status == searchText)
    else:
        issuesQuery = db.session.query(IssuesIssues)
    issues: list[IssuesIssues] = issuesQuery.order_by(IssuesIssues.created_at.desc())\
        .paginate(pageNumber, per_page=pageSize, error_out=False).items
    issueList = []
    for issue in issues:
        issue = issue.__dict__
        issue.pop('_sa_instance_state')
        issue['created_at'] = issue['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        issueList.append(issue)
    return jsonify({"total": issuesQuery.count(), "rows": issueList})


@console.route('/issues/edit', methods=['POST'])
def issues_edit():
    try:
        req_id = request.values.get('id')
        req_status = request.values.get('status')
        print(req_id, req_status)
        db.session.query(IssuesIssues).filter(IssuesIssues.id == req_id).update(
            {'status': req_status})
        db.session.commit()
        return jsonify({"status": 200, "msg": '操作成功'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify({"status": 499, "msg": '操作失败'})


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
