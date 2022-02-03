from flask import g
from studio.models import ChatBody, ChatHead, db


def send_chat(from_id='', to_id='', text='', head=-1):
    b = ChatBody(msg_from=from_id, msg_to=to_id, msg_text=text, head=head)
    db.session.add(b)
    db.session.commit()
    return b


def start_chat(first, second, first_alias=None, second_alias=None):
    head = ChatHead.query.filter((ChatHead.first == g.user.id) | (ChatHead.second == g.user.id)).first()
    if head:
        return head.id
    h = ChatHead(first=first, second=second, first_alias=first_alias, second_alias=second_alias)
    db.session.add(h)
    db.session.commit()
    return h.id
