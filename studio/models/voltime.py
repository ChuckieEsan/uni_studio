from .base import db, MixinBase


class VoltimeOld(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(5), nullable=False)
    faculty = db.Column(db.String(5), nullable=False)
    stu_id = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    activity_name = db.Column(db.Text, nullable=False)
    activity_faculty = db.Column(db.Text, nullable=False)
    team = db.Column(db.Text, nullable=False)
    activity_time = db.Column(db.Text, nullable=False)
    duty_person = db.Column(db.Text, nullable=False)


class Voltime(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(5), nullable=False)
    faculty = db.Column(db.String(20), nullable=False)
    stu_id = db.Column(db.BigInteger, nullable=False)
    duration = db.Column(db.DECIMAL(5, 2), nullable=False)
    activity_name = db.Column(db.String(50), nullable=False)
    activity_faculty = db.Column(db.String(20), nullable=False)
    team = db.Column(db.String(50), nullable=False)
    activity_date_str = db.Column(db.String(30), nullable=False, default="")
    activity_DATE = db.Column(db.DATE, nullable=False)
    duty_person = db.Column(db.String(20), nullable=False)
    remark = db.Column(db.Text, nullable=False)


class VoltimeDupname(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    dupNum = db.Column(db.SmallInteger, nullable=False)
    edit_by = db.Column(db.Integer, nullable=False)
