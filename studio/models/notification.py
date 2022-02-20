from .base import db, MixinBase


class NotificationsGlobal(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    valid_until = db.Column(db.DateTime(True), default=db.func.now(), nullable=False)
    created_by = db.Column(db.Integer)
    path = db.Column(db.Text, nullable=True, default='/')

    def __init__(self, kwargs=dict()):
        for k in kwargs:
            setattr(self, k, kwargs[k])
