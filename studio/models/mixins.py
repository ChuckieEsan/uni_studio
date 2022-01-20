from sqlalchemy.event import listens_for

from .base import db


class TimestampMixin(object):
    updated_at = db.Column(db.DateTime(True), default=db.func.now(), nullable=False)
    created_at = db.Column(db.DateTime(True), default=db.func.now(), nullable=False)


class DeleteMixin(object):
    delete = db.Column(db.Boolean, default=False, nullable=False)
