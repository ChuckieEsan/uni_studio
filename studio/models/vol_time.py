from .base import db
from .mixins import TimestampMixin, DeleteMixin


class VolTime(db.Model):
    __tablename__ = "vol_time"
    id = db.Column(db.Integer, primary_key=True,nullable=False)
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
