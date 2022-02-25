from flask import Blueprint, jsonify, request, jsonify, current_app, g
from studio.models import IssueTypes, IssueIssues, db, UserUsers
from studio.utils.send_chat import send_chat, start_chat
from studio.utils.send_mail import send_mail

issue = Blueprint('issue', __name__, url_prefix='/issue')


@issue.route('/', methods=['GET', 'POST'])
def dayImage_cata():
    if request.method == 'GET':
        referer = request.referrer if request.referrer is not None else ''
        resTypes = db.session.query(IssueTypes.typename).order_by(IssueTypes.priority.desc()).all()
        return jsonify({'referer': referer, 'lstTypes': [issuetype[0] for issuetype in resTypes]})
    if request.method == 'POST':
        req = request.get_json()
        issue = IssueIssues(ip=request.remote_addr,
                            url=req['referer'],
                            type=req['type'],
                            contact=req['contact'],
                            name=req['name'],
                            stu_id=req['stu_id'],
                            content=req['content'],
                            user_id=None if not g.user else g.user.id)
        db.session.add(issue)
        db.session.commit()

        # resDutyUsers:str = db.session.query(IssueTypes.duty_user)\
        #     .filter(IssueTypes.typevalue == req['type']).scalar()
        # lstUserID = resDutyUsers.split(',')
        # for userID in lstUserID:
        #     to = db.session.query(UserUsers.email).filter(UserUsers.id == userID).scalar()
        #     send_mail(to=to, content=str(issue), subject='dutbit.com 新增反馈通知', type='plain')

        print(req['type'])
        resDutyUserID:int = db.session.query(IssueTypes.duty_user)\
            .filter(IssueTypes.typevalue == req['type']).scalar()
        to = db.session.query(UserUsers.email).filter(UserUsers.id == resDutyUserID).scalar()
        print(resDutyUserID,to)
        send_mail(to=to, content=str(issue), subject='dutbit.com 新增反馈通知', type='plain')

        # if g.user:
        #     to = UserUsers.query.filter(UserUsers.role_bits.op('&')(1) == 1).first()
        #     head = start_chat(g.user.id, to.id, first_alias=g.user.email, second_alias='反馈处理')
        #     send_chat(from_id=g.user.id, text='查看反馈工单{}'.format(issue.id), to_id=to.id, head=head)
        # flash('提交成功，感谢您的反馈')
        # return redirect(url_for('issues.root', timeout=True))

        return "ok"