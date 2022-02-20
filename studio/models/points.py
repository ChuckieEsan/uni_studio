from .base import db, MixinBase


class Points(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(5), nullable=False, default='')
    faculty = db.Column(db.String(20), nullable=False, default='')
    stu_id = db.Column(db.BigInteger, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    remark = db.Column(db.Text, nullable=False, default='')
