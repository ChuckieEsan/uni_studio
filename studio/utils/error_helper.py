from flask import render_template, flash, current_app, request
from werkzeug.exceptions import HTTPException, Unauthorized, InternalServerError, Forbidden, NotFound, BadRequest, ServiceUnavailable


def error_handler(e):
    if isinstance(e,HTTPException):
        current_app.logger.error('http-error:'+str(e.code)+':'+request.path)
    if isinstance(e, Unauthorized):
        return render_template('common_error.html', code=e.code, msg='无权访问本页面')
    if isinstance(e, InternalServerError):
        return render_template('common_error.html', code=e.code, msg='发生了错误')
    if isinstance(e, BadRequest):
        return render_template('common_error.html', code=e.code, msg='无法处理的信息')
    if isinstance(e, NotFound):
        return render_template('common_error.html', code=e.code, msg='要访问的页面找不到了，但我们可以复习一下傅里叶变换')
    if isinstance(e, Forbidden):
        return render_template('common_error.html', code=e.code, msg='本页面禁止访问')
    if isinstance(e, ServiceUnavailable):
        return render_template('common_error.html', code=e.code, msg='服务维护中，请稍后再试')
    return render_template('common_error.html', code=500, msg='遇到了错误')
