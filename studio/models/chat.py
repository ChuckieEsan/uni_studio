from .base import db
from .mixins import TimestampMixin


class ChatHead(db.Model,TimestampMixin):
    __tablename__ = "chat_head"
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.Integer)
    second = db.Column(db.Integer)
    def __init__(self,*args,**kwargs):
        super(ChatBody, self).__init__(**kwargs)

class ChatBody(db.Model,TimestampMixin):
    __tablename__ = "chat_body"
    id = db.Column(db.Integer, primary_key=True)
    head = db.Column(db.Integer,nullable=False)
    msg_from = db.Column(db.Integer,nullable=False)
    msg_to = db.Column(db.Integer,nullable=False)
    msg_text = db.Column(db.Text) 
    def __init__(self,*args,**kwargs):
        super(ChatBody, self).__init__(**kwargs)
    pass