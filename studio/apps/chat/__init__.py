from flask import Blueprint
from flask.globals import request
from flask.helpers import url_for
from flask.templating import render_template
from flask import g
from sqlalchemy.sql.expression import text
from werkzeug.utils import redirect
from studio.models import ChatBody, ChatHead, db, UserUsers
from studio.utils.send_chat import send_chat, start_chat

chat = Blueprint("chat", __name__, template_folder="templates", static_folder="static")


@chat.route('/')
def chat_index():
    heads = ChatHead.query.filter((ChatHead.first == g.user.id) | (ChatHead.second == g.user.id)).all()
    return render_template('chat_index.html', chats=heads)


@chat.route('/', methods=['POST'])
def chat_start():
    to = UserUsers.query.filter(UserUsers.email == request.values['to']).first()
    head = start_chat(g.user.id, to.id, first_alias=g.user.email, second_alias=to.email)
    send_chat(from_id=g.user.id, text=request.values['text'], to_id=to.id, head=head)
    return redirect(url_for('chat.chat_index'))


@chat.route('/<int:head_id>')
def chat_room(head_id):
    chats = ChatBody.query.filter(ChatBody.head == head_id).all()
    head = ChatHead.query.filter(ChatHead.id == head_id).first_or_404()
    to = head.first if head.second == g.user.id else head.second
    print(to)
    return render_template('chat_room.html', chats=chats, head=head, to=to)


@chat.route('/<int:head_id>', methods=['POST'])
def chat_room_send(head_id):
    send_chat(from_id=g.user.id, to_id=int(request.values['to'].strip()), text=request.values['text'], head=head_id)
    return redirect(url_for('chat.chat_room', head_id=head_id))
