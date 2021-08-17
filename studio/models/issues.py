from .base import db
from .mixins import TimestampMixin


class IssuesIssues(TimestampMixin, db.Model):
    __tablename__ = 'issues_issues'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(255), nullable=True)
    contact = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(20), nullable=True)
    stu_id = db.Column(db.BigInteger, nullable=True)
    content = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), default='pending', nullable=True)

    def __init__(self, *args, **kwargs):
        super(IssuesIssues, self).__init__(**kwargs)

    def __str__(self):
        return f"<IssueIssue NO {self.id}>\n类型：{self.type}\n联系方式：{self.contact}\n姓名：{self.name}\n学号：{self.stu_id}\n反馈内容：\n{self.content}"


class IssueTypes(TimestampMixin, db.Model):
    __tablename__ = 'issues_types'
    id = db.Column(db.Integer, primary_key=True)
    default = db.Column(db.Boolean, default=False, nullable=False)
    typename = db.Column(db.String(255), nullable=False)
    typevalue = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.Integer, default=1)
    duty_user = db.Column(db.Integer)
    created_by = db.Column(db.String(255), nullable=False)  # creator object_id

    def __init__(self, *args, **kwargs):
        super(IssueTypes, self).__init__(**kwargs)

    def __str__(self):
        return "<IssueType NO {}> {} -> {}"\
            .format(self.id, self.typename, self.typevalue)
