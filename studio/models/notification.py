from .base import db
from .mixins import TimestampMixin

class GlobalNotifications(db.Model,TimestampMixin):
    __tablename__ = "notifications_global"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    valid_until = db.Column(db.DateTime(True), default=db.func.now(), nullable=False)
    created_by = db.Column(db.Integer)
    path = db.Column(db.Text,nullable=True,default='/')