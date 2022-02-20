from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class MixinBase(object):
    created_at = db.Column(db.DateTime(True), nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime(True), nullable=False, default=db.func.now(), onupdate=db.func.now())
    deleted = db.Column(db.Boolean, nullable=False, default=False)


class EditHistory(db.Model, MixinBase):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    table_name = db.Column(db.String(30), nullable=False)
    row_id = db.Column(db.Integer, nullable=False)
    rows_total = db.Column(db.SmallInteger, nullable=False, default=1)
    attr_name = db.Column(db.String(30), nullable=False, default='')
    details = db.Column(db.Text, nullable=False, default='')
    edit_by = db.Column(db.Integer, nullable=False)
