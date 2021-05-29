from flask import Blueprint
from flask.globals import request
from flask.helpers import url_for
from flask.templating import render_template
from flask import g
from werkzeug.utils import redirect
from studio.models import ChatBody, ChatHead, db,UserUsers
from studio.utils.send_chat import send_chat,start_chat
chat = Blueprint("chat", __name__, template_folder="templates",
                 static_folder="static")


@chat.route('/')
def chat_index():
    chats = ChatBody.query.filter((ChatBody.msg_from == g.user.id) | (
        ChatBody.msg_to == g.user.id)).distinct().all()
    return render_template('chat_index.html', chats=chats)


@chat.route('/', methods=['POST'])
def chat_start():
    to_id = UserUsers.query.filter(UserUsers.email==request.values['to']).first().id
    head = start_chat(g.user.id,to_id)
    send_chat(
        from_id=g.user.id,
        text=request.values['text'],
        to_id=to_id,
        head=head
    )
    return redirect(url_for('chat.chat_index'))
