from werkzeug.security import check_password_hash, generate_password_hash
from .base import db, MixinBase


class UserUsers(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(100), nullable=True, unique=True)
    wx_openid = db.Column(db.String(100), nullable=False,default='')
    password_hash = db.Column(db.String(150), nullable=False)
    role_bits = db.Column(db.Integer, default=2)
    validation_code = db.Column(db.Text,default='')
    validated = db.Column(db.Boolean,default=True)
    current_ip = db.Column(db.String(100), nullable=True)
    last_login_ip = db.Column(db.String(100), nullable=True)
    last_login_time = db.Column(db.DateTime(True), default=db.func.now(), nullable=True)

    def __init__(self, kwargs=dict()):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def password(self):
        raise AttributeError('明文密码不可读')

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# 设计缺陷：roles应该有个uuid字段确保并发操作不会出问题
class UserRoles(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    role_bit = db.Column(db.Integer, nullable=False, unique=True)  # should be unique
    created_by = db.Column(db.Integer, default=1)  # user_users.id
    role_text = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, kwargs=dict()):
        for k in kwargs:
            setattr(self, k, kwargs[k])


class UserGroups(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)


class UserGroupMembers(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    group_id = db.Column(db.Integer)
