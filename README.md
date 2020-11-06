# uni_studio
[![Build Status](https://travis-ci.org/dutbit/uni_studio.svg?branch=main)](https://travis-ci.org/dutbit/uni_studio)  
A web based set of tools for operations of studios in universities.

- User service  
    Currently a golang project with mongodb storage and sessions over redis, aiming to provide flexibility and single-sign-on service.  
    `The entire "uni_studio" project is heavily coupled with userservice.`
- Enroll  
    A recruitment platform featuring highly configurable sign-up forms.
    
- File service  
    Forked from the  "flask-file-uploader", providing minimal support for studio-wide small file sharing.

- Members  
    An information management system aiming at taking full grasp of members' relevant info, supporting multi-format xlsx/csv exports, making everyone's lives easier.

- Album  
    A photo-sharing platform providing support for propaganda work of the CCYL.

- Vote  
    Customizable voting.

## known issues
- 应该是因为app的server name没配置，有不少url_for的跳转是跳回127.0.0.1的
- votes新建vote的图挂了
## todo
- 添加config（今晚）
