import os
from studio.utils.cos import cos_put, url_for_cos
from studio.utils.hash_helper import md5
from .init import console
from flask import render_template, redirect, request, abort, g, url_for, current_app
from studio import models
import datetime
from sqlalchemy import inspect
import time
URL_PATTERN_RU = '/crud/<string:table>'
URL_PATTERN_CD = '/crud/cd/<string:table>'


def get_class(table_name: str):
    if not table_name:
        return None
    target_class = None
    for _class in models.__all__:
        if hasattr(_class, '__tablename__') and _class.__tablename__ == table_name:
            target_class = _class
            break
    return target_class


@console.route('/crud')
def crud_root():
    return render_template('crud_index.html', models=models)


@console.route(URL_PATTERN_RU, methods=['GET'])
def crud_get(table):
    target_class = get_class(table)
    if not target_class:
        return redirect(url_for('console.console_root'))
    current_app.logger.info(target_class)
    _id = request.values.get('id')
    if _id:
        all = target_class.query.filter(getattr(target_class, 'id') == _id).all()
    else:
        all = target_class.query.all()

    insp = inspect(models.db.engine)
    columns = insp.get_columns(table)
    constraints = {}
    for c in columns:
        constraints[c['name']] = None
        _type = str(c['type']).lower()
        if _type in ['integer', 'text'] or 'varchar' in _type or 'integer' in _type:
            constraints[c['name']] = 'file' if 'image' in c['name'] else 'text'
        elif _type == 'boolean' or _type == "tinyint(1)":
            constraints[c['name']] = 'bool'
        elif _type == "datetime":
            constraints[c['name']] = 'datetime'
    return render_template('common_crud.html',
                           data=all,
                           _class=target_class,
                           constraints=constraints,
                           getattr=getattr,
                           title="crud")


@console.route(URL_PATTERN_RU, methods=['POST'])
def crud_put(table):
    target_class = get_class(table)
    if not target_class:
        return redirect(url_for('console.console_root'))
    insp = inspect(models.db.engine)
    columns = insp.get_columns(table)
    constraints = {}
    for c in columns:
        constraints[c['name']] = str(c['type']).lower()

    key = request.values['key']
    dkey = request.values['dtype']
    if not dkey:
        print('not dkey')
        abort(500)
    value = request.files[dkey] if dkey == "file" else request.values[dkey]
    key_constraint = constraints[key]
    if key_constraint == 'boolean' or key_constraint == 'tinyint(1)':
        value = False if value != '1' else True
    elif key_constraint == "integer":
        value = int(value)
    elif key_constraint == "datetime":
        value = datetime.datetime.strptime(value, r"%H:%M %m/%d/%Y")
    if dkey == "file":
        _, fname = cos_put(value)
        value = url_for_cos(fname)

    _id = request.values['id']
    if key is None or value is None:
        abort(500)
    data = target_class.query.filter(getattr(target_class, 'id') == _id).first()
    if data:
        setattr(data, key, value)
        models.db.session.commit()
    if request.args.get('id'):
        return redirect(url_for('console.crud_get', table=table, id=_id))
    else:
        return redirect(url_for('console.crud_get', table=table))


@console.route(URL_PATTERN_CD, methods=['GET'])  # 删除
def crud_delete(table):
    _id = request.values.get('id')
    target_class = get_class(table)
    item = target_class.query.filter(getattr(target_class, 'id') == _id).first()
    models.db.session.delete(item)
    models.db.session.commit()
    return redirect(url_for('console.crud_get', table=table))


@console.route(URL_PATTERN_CD, methods=['POST'])  # 添加
def crud_create(table):
    attrs = {}
    for k in request.values:
        if request.values[k] != '':
            attrs[k] = request.values[k]
    target_class = get_class(table)
    obj = target_class(kwargs=attrs)
    print(obj.__dict__)
    models.db.session.add(obj)
    models.db.session.commit()
    return redirect(url_for('console.crud_get', table=table))
