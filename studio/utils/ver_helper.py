from flask import current_app


def get_ver():
    return current_app.config.get('VERSION')
