from .base import db, MixinBase


class ChatHead(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.Integer)
    second = db.Column(db.Integer)
    first_alias = db.Column(db.Text)
    second_alias = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)


class ChatBody(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    head = db.Column(db.Integer, nullable=False)
    msg_from = db.Column(db.Integer, nullable=False)
    msg_to = db.Column(db.Integer, nullable=False)
    msg_text = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
