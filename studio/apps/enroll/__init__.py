from flask import Blueprint
from flask import render_template
enroll = Blueprint("enroll", __name__, template_folder="templates")

customItems = [
    {"id": "1", "label": "test1", "name": "test1", "info": "testInfo"},
    {"id": "1", "label": "test1", "name": "test1", "info": "testInfo"},
    {"id": "1", "label": "test1", "name": "test1", "info": "testInfo"},
    {"id": "1", "label": "test1", "name": "test1", "info": "testInfo"},
]  #debug
"""
    设计的自定义内容格式,默认组件类型:text
    id: id
    label: 属性名
    name: name
    info: placeholder
    necessity: 是否必需
"""


@enroll.route('/')
def enroll_index():
    return render_template("signup.html", customItems=customItems)
