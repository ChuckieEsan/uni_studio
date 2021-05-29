# studio

[![Build Status](https://travis-ci.org/dutbit/uni_studio.svg?branch=main)](https://travis-ci.org/dutbit/uni_studio)  
DUTBIT web服务主仓库

## 项目结构

├─.github  
│  └─workflows  `github workflow,用于CI`  
├─data  
│  └─fileservice  `个人文件存储`  
│      ├─1  `uid`  
│      └─thumbnail `缩略图`  
│        &nbsp;&nbsp;&nbsp;&nbsp;  └─1  `uid`  
├─log  `uwsgi log`  
├─migrations  `flask-migrate数据库版本迁移`  
│  ├─versions  
├─studio  
│  ├─api  `无模板渲染的纯接口`  
│  │  ├─postcard  `校庆70周年有声明信片小程序`  
│  │  │  ├─templates  `小程序内部管理用模板`  
│  ├─apps `所有对外服务的apps，每个文件夹是一个Blueprint`  
│  │  ├─common  `公用文件，如模板、静态图片资源`  
│  │  │  ├─static  
│  │  │  │  ├─cos  `本地简易对象存储,文件名是对文件内容的sha256`  
│  │  │  │  │  └─thumbnails  `图片缩略图`  
│  │  │  │  ├─css  `公有css`  
│  │  │  │  ├─img  `公有图片，如各种icon`
│  │  │  │  ├─js  `公有js`  
│  │  │  │  └─uploads  `原有uploads，已弃用，保持向下兼容`  
│  │  │  ├─templates  `公有html模板和报错模板`  
│  │  ├─console  `网站后台控制台`  
│  │  ├─enroll  `招新`  
│  │  ├─fileservice  `个人文件存储，基于flask-file-upload`  
│  │  ├─h5  `h5项目，72周年贺卡生成`  
│  │  ├─issues  `用户反馈入口`  
│  │  ├─members  `规划中，实际为社团管理`
│  │  ├─users  `用户登陆/注册/找回密码/邮箱验证`  
│  │  ├─vol_time  `志愿时长查询`  
│  │  ├─vote  `投票系统`  
│  ├─cache  `flask-cache`  
│  ├─cos  `对象存储`  
│  ├─interceptors  `拦截器，负责请求鉴权`  
│  ├─models  `SQLAlchemy数据库模式`  
│  ├─utils  `内部帮助函数`  
├─tests  `pytest`

## 开发须知

### 安装依赖

- `pip install -r requirements.txt`
- `python serve.py`
  
### 数据库模式更新

- `flask db migrate`
- `flask db upgrade`
- 参考[这篇文章](http://www.ttlsa.com/python/flask-migrate-management-database-upgrade-and-migrate/)
- 审查sql：`flask db upgrade --sql`
- sqlite本地开发无法drop column：参考[this](https://blog.csdn.net/White_Idiot/article/details/78533046)

### 更新python依赖

- `pipreqs --encoding utf8 --force .`

### 添加service到systemd

- `vim /usr/lib/systemd/system/studio.service`

### 验证码服务

- 使用了[recaptcha](https://pypi.org/project/Flask-hCaptcha/)
