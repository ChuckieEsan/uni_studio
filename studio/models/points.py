from .base import db
from .mixins import TimestampMixin, DeleteMixin
from sqlalchemy import text


class Points(db.Model):
    __tablename__ = "points"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False, server_default='')
    sex = db.Column(db.String(5), nullable=False, server_default='')
    faculty = db.Column(db.String(20), nullable=False, server_default='')
    stu_id = db.Column(db.BigInteger, nullable=False, server_default=text('0'))
    points = db.Column(db.Integer, nullable=False, server_default=text('0'))
    remark = db.Column(db.Text, nullable=False)
