from .base import db, MixinBase


class RouteInterceptors(db.Model, MixinBase):
    id = db.Column(db.Integer, primary_key=True)
    startswith = db.Column(db.String(100), nullable=False)
    role_bits = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, default=1)  # user_users.id
    description = db.Column(db.Text, nullable=True)
