from .base import db
from .mixins import TimestampMixin,DeleteMixin

class NotesNotes(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    group_id = db.Column(db.Integer,nullable=True)
    create_time = db.Column(db.Integer,nullable=True)
    update_time = db.Column(db.Integer,nullable=True)
    query_key = db.Column(db.Text,nullable=True)
    tags = db.Column(db.Text,nullable=True)
    content = db.Column(db.Text,nullable=True)
    front = db.Column(db.Boolean,nullable=True)
    alert = db.Column(db.Boolean,nullable=True)
    alert_time = db.Column(db.Integer,nullable=True)
    uid = db.Column(db.String(33),nullable=False)