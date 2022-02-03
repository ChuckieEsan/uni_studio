from .base import db
import time


class PostcardUsers(db.Model):
    __tablename__ = 'postcard_users'
    id = db.Column(db.Integer, primary_key=True)
    wxid = db.Column(db.String(65), nullable=True)
    wx_name = db.Column(db.String(100), nullable=True)
    last_ip = db.Column(db.String(100), nullable=False)
    log_time = db.Column(db.Integer, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('postcard_roles.id'))
    cards_saved = db.Column(db.Text, nullable=True)
    avt_url = db.Column(db.String(200), nullable=True)

    def __init__(self, wxid, last_ip, role_id=2, wx_name=None, cards_saved='[]', avt_url=''):
        self.wxid = wxid
        self.wx_name = wx_name
        self.last_ip = last_ip
        self.log_time = int(time.time())
        self.role_id = role_id
        self.cards_saved = cards_saved
        self.avt_url = avt_url


class PostcardCards(db.Model):
    __tablename__ = 'postcard_cards'
    id = db.Column(db.Integer, primary_key=True)
    wx_openid = db.Column(db.String(100))
    create_time = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    with_audio = db.Column(db.Integer, nullable=True)  # 0是采用自带模板，非0是模板编号
    with_img = db.Column(db.Integer, nullable=True)  # 0是采用自带模板，非0是模板编号
    dir_name = db.Column(db.String(33), nullable=True)
    crop = db.Column(db.Text, nullable=True)
    display = db.Column(db.Boolean, nullable=False)
    likes = db.Column(db.Integer, nullable=True)
    liked_by = db.Column(db.Text, nullable=True)

    def __init__(self,
                 wx_openid,
                 title,
                 description,
                 content,
                 crop='',
                 with_audio=0,
                 with_img=0,
                 display=False,
                 dir_name='',
                 likes=0,
                 liked_by='[]'):
        self.wx_openid = wx_openid
        self.title = title
        self.description = description
        self.content = content
        self.crop = crop
        self.with_audio = with_audio
        self.with_img = with_img
        self.display = display
        self.create_time = int(time.time())
        self.dir_name = dir_name
        self.likes = likes
        self.liked_by = liked_by


class PostcardTemplates(db.Model):
    __tablename__ = 'postcard_templates'
    id = db.Column(db.Integer, primary_key=True)
    upload_user = db.Column(db.Integer, db.ForeignKey('postcard_users.id'))
    create_time = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    with_audio = db.Column(db.Boolean, nullable=True)

    def __init__(self, upload_user, create_time, title, description, with_audio):
        self.upload_user = upload_user
        self.create_time = int(time.time())
        self.title = title
        self.description = description
        self.with_audio = with_audio


class PostcardRoles(db.Model):
    __tablename__ = 'postcard_roles'
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, creator, name, description):
        self.name = name
        self.creator = creator
        self.description = description
        self.create_time = int(time.time())
