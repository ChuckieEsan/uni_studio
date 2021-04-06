from .base import db
from .mixins import TimestampMixin, DeleteMixin


class EnrollCandidates(db.Model, TimestampMixin, DeleteMixin):
    __tablename__ = "enroll_candidates"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(5), nullable=False)
    major = db.Column(db.String(100))
    specialty = db.Column(db.Text)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(30))
    intro = db.Column(db.Text)
    details = db.Column(db.Text)
    status = db.Column(db.Integer, default=0)
    ip = db.Column(db.String(100))

    def __init__(self, *args, **kwargs):
        super(EnrollCandidates, self).__init__(**kwargs)

    def __str__(self):
        return "<Vote NO {}>".format(self.id)


class EnrollForms(db.Model, TimestampMixin, DeleteMixin):
    __tablename__ = "enroll_forms"
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    details = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(EnrollForms, self).__init__(**kwargs)

    def __str__(self):
        return "<Vote NO {}>".format(self.id)
