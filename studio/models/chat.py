from .base import db
from .mixins import TimestampMixin


class ChatHead(db.Model,TimestampMixin):
    __tablename__ = "chat_head"
    id = db.Column(db.Integer, primary_key=True)

class ChatBody(db.Model,TimestampMixin):
    __tablename__ = "chat_body"
    id = db.Column(db.Integer, primary_key=True)
    head = db.Column(db.Integer,nullable=False)
    msg_from = db.Column(db.Integer,nullable=False)
    msg_to = db.Column(db.Integer,nullable=False)
    msg_text = db.Column(db.Text) 
    pass