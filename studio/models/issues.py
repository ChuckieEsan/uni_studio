from .base import db
from .mixins import TimestampMixin
class IssuesIssues(TimestampMixin,db.Model):
    __tablename__='issues_issues'
    id = db.Column(db.Integer,primary_key=True)
    status = db.Column(db.String(255),default='pending',nullable=True)
    ip = db.Column(db.String(100),nullable=False)
    url = db.Column(db.Text,nullable=True)
    contact = db.Column(db.Text,nullable=True)
    type = db.Column(db.String(255),nullable=True)
    content = db.Column(db.Text,nullable=True)
    user_id = db.Column(db.String(255),nullable=True)
