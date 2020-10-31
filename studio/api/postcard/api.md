流程：

### 登录操作流程

- 前端：调用wx.login,拿到code，json编码【POST】给后端【/postcard/access】“{code:abc123}”
  
- 后端：访问微信api，拿到openid，作为身份凭据，

    数据库中查找openid，如果没有则插入数据库，同时新建用户目录以及用户临时目录  

    返回json“{'success':0,'exist':0,'data':'','errorCode':0}”
        请求成功：{'success':1,'data':{openid:'xxxyyyzzz'},'errorCode':0,new:0}
        请求失败：{'success':0,'data':{'errorMsg':'失败原因xxx'},'errorCode':1,new:0}
            新用户：{。。。new：1}

- 前端：将拿到的openid存在（用户）本地存储中
        如果是新用户，则【GET】后端【/postcard/role】拿role list让用户明确身份（校友，在校。。。）。  该身份信息是否允许用户随时修改？
        【PUT】后端【/postcard/access】给后端修改
- 后端：修改后{success:1,msg:成功提示xxx}失败返回{success:0,msg:失败原因xxx}



### 用户新建一张明信片

如果选择使用模板，只需用户输入from to 信息 +  正文/语音就行  实际上所谓模板只提供封面图片<font color="red">( 封面图里要不要语音 像示例小程序那样？ )</font>

- 前端：
    选择1：背景图是用模板（给用户预览图）还是自己的图，【模板接口类似这个：http://www.dutbit.com:6060/postcard/template/1?target=image&size=small】size有large和small可选，target有image和audio可选
    如果选模板则【GET】后端【/postcard/template/（id）】，header里面加token:【openid】
    如果是自己的图则开上传，【POST】后端【/postcard/upload】，具体请求：
        请求body里面加json{type：'image'}，header里面加token:【openid】

- 前端：选择2：音频是用模板还是自己录，如果是自己录的则开上传,【POST】后端【/postcard/upload】，具体请求：
    请求body里面加json{type：'audio'}，header里面加token:【openid】

- 前端：最终提交用户剩余信息json格式，【POST】后端【/postcard/card】包括content，title（明信片的抬头）,audio(bool),img(bool),
header里面加token:【openid】

- 后端：GET 了template之后以openid鉴权，由python负责返回数据【可能要改，不确定能不能在一个响应里能不能放音频和图片】<font color="red">返回文件路径就行</font>

- 后端：把拿到的图存进用户临时目录，成功返回{success:1,msg:成功提示xxx}失败返回{success:0,msg:失败原因xxx}

- 后端：把拿到的音频存进用户临时目录，成功返回{success:1,msg:成功提示xxx}失败返回{success:0,msg:失败原因xxx}


- 后端：存数据库，成功返回{success:1,msg:成功提示xxx}失败返回{success:0,msg:失败原因xxx}



### 用户打开一张明信片

- 前端：拿到明信片的id（主要靠微信分享的url来实现，比如id=888）###注，<font color="red">【待讨论】这里默认用户已经打开小程序，即能拿到openid </font>  
【GET】后端【/postcard/card/（id）】，header里面加token:【openid】（不加也放行）
    
- 后端：凭id读数据库内容，返回json内容，{success:1,msg:成功提示xxx，data：该card的信息}失败返回{success:0,msg:失败原因xxx}，
    data里面包括wx_name和with_audio,with_img,

- 前端：按后端返回内容请求音频，图片资源【/postcard/image/（id）】【/postcard/audio/（id）】
  
- 前端：如果发现该card的wx_openid==【openid】则给人编辑权限，编辑方法用【PUT】，具体请求同新建


### 用户查看自己建立的所有明信片，（类似大厅，可以写成同一个界面）
- 前端：【GET】后端【/postcard/home】，header里面加token:【openid】

- 后端：返回该用户所有card信息的json数组

- 前端：按拿到的json数组每个card的id【GET】后端【/postcard/mini_image/（id）】拿缩略图

- 后端:直接返回图



### 用户保存明信片  收到后可选择保存  保存的所有明信片可以在小程序个人页查看 ？

### 创建模板接口?

###  公共区域 ， 用户发送的明信片可投放到此，所有人可以浏览 ？


音频  MP3?  wav?
图片后端压缩 ？ 

先把这个写出来？ 