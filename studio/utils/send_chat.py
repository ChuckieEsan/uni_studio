from flask import g
from studio.models import ChatBody,ChatHead,db

def send_chat(from_id='',to_id='',text=''):
    b = ChatBody(
        msg_from=from_id,
        msg_to=to_id,
        msg_text =text
        )
    db.session.add(b)
    db.session.commit()
    return

def start_chat(first,second):
    h = ChatHead(
        first=first,
        second=second
    )
    db.session.add(h)
    db.session.commit()
    return h.id