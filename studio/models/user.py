from .base import db
from .mixins import TimestampMixin, DeleteMixin


class UserUsers(db.Model, TimestampMixin, DeleteMixin):
    __tablename__ = "user_users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(100), nullable=True, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role_bits = db.Column(db.Integer, default=2)
    current_ip = db.Column(db.String(100), nullable=True)
    last_login_ip = db.Column(db.String(100), nullable=True)
    last_login_time = db.Column(db.DateTime(True), default=db.func.now(), nullable=True)
    confirmed = db.Column(db.Boolean)
    objid = db.Column(db.String(100), nullable=True)
    validation_code = db.Column(db.Text)

    def __init__(self, kwargs=dict()):
        for k in kwargs:
            setattr(self, k, kwargs[k])


# 设计缺陷：roles应该有个uuid字段确保并发操作不会出问题


class UserRoles(db.Model, TimestampMixin, DeleteMixin):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer, primary_key=True)
    role_bit = db.Column(db.Integer, nullable=False, unique=True)  # should be unique
    created_by = db.Column(db.Integer, default=1)  # user_users.id
    role_text = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, kwargs=dict()):
        for k in kwargs:
            setattr(self, k, kwargs[k])


class UserGroups(db.Model, TimestampMixin, DeleteMixin):
    __tablename__ = "user_groups"
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)


class UserGroupMembers(db.Model, TimestampMixin, DeleteMixin):
    __tablename__ = "user_groups_members"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    group_id = db.Column(db.Integer)
