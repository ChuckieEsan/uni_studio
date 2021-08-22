from .base import db
from .mixins import TimestampMixin, DeleteMixin


class VolTime_old(db.Model):
    __tablename__ = "vol_time_old"
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


class VolTime(db.Model):
    __tablename__ = "vol_time"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(5), nullable=False)
    faculty = db.Column(db.String(20), nullable=False)
    stu_id = db.Column(db.BigInteger, nullable=False)
    duration = db.Column(db.DECIMAL(5, 2), nullable=False)
    activity_name = db.Column(db.String(50), nullable=False)
    activity_faculty = db.Column(db.String(20), nullable=False)
    team = db.Column(db.String(50), nullable=False)
    activity_date_str = db.Column(db.String(30), nullable=False)
    activity_DATE = db.Column(db.DATE, nullable=False)
    duty_person = db.Column(db.String(20), nullable=False)
    remark = db.Column(db.Text, nullable=False)


class VolTime_edit(TimestampMixin, db.Model):
    __tablename__ = "vol_time_edit"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    vol_time_id = db.Column(db.Integer, nullable=False)
    name_ori = db.Column(db.String(20), nullable=False)
    stu_id_ori = db.Column(db.BigInteger, nullable=False)
    name_new = db.Column(db.String(20), nullable=False)
    stu_id_new = db.Column(db.BigInteger, nullable=False)
    edit_by = db.Column(db.Integer, nullable=False)


class VolTime_dupName(TimestampMixin, db.Model):
    __tablename__ = "volTime_dupName"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    dupNum = db.Column(db.SmallInteger, nullable=False)
    edit_by = db.Column(db.Integer, nullable=False)
