from studio.models import UserRoles, db


def and_op(a, b):
    return int(a) & int(b)


def setup_roles():
    root = UserRoles.query.filter(UserRoles.role_bit == 1).first()
    if not root:
        r = UserRoles()
        r.role_text = 'root'
        r.description = 'root'
        db.session.add(r)
        db.session.commit()
