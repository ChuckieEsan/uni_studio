### 登录操作流程
- /postcard/code `POST`
> {code:abc123xyz}  
> 返回：msg = {'success':1,'data':{token:aaabbbcccdddeee},'errorCode':0,'new':0}  
如果success=0，可以看errorcode，报错信息字符串在data里  
如果new=1则表示新用户且已记录进数据库
- /postcard/user `GET,PUT`  
<font color="orange">必须带header的openid头，且已在数据库中</font>
> GET：直接请求  
msg['data'] = {'user_cards':已有明信片的数组,'user_saves':已保存的其他明信片id，以逗号分隔，需要前端自行分割};msg['success']=1  

>PUT:  
请求体：{cards_saved:'1,3,5,67,5655'}
返回：msg{success:1/0}

- /postcard/card `POST,GET`  
>GET: url传参  
/postcard/card?id=3
返回：成功则success=1,data=json  
`{"data":{"content":"content","create_time":1585974046,"crop":"9x9x9x9","description":"desc1","dir_name":"1585974046-53728ffb6ce39a064","display":true,"id":3,"title":"title","with_audio":0,"with_img":0,"wx_openid":"asdf"},"errorCode":0,"success":1}`  
<font color="orange">此处已经拿到静态资源地址，可以直接请求，`www.dutbit.com/static/uploads/【wx_openid】/【dir_name】/【large.png,small.png,audio.mp3】`</font>  

>POST: 请求体json编码，<font color="orange">需要带openid的headers</font>  
<font color="orange">crop字段暂时不用可留空，注意with_audio和img是int，0代表采用已上传的用户自定义资源，1、2、…代表采用模板id==1，2，3；display是bool</font>  
`{"content":"content",
"crop":"9x9x9x9",
"display":true,
"wx_openid":"asdf",
"title":"title",
"description":"desc1",
"with_audio":0,
"with_img":0}`  成功会返回{success:1,...,id:x}

- /postcard/templates `GET`
> 直接请求，返回可用的全部模板的json数组  
{success:1,data:[那个数组]}

- /postcard/public `GET`
> 直接请求，返回所有人可见的card list  
{success:1,data:[那个数组]}

- /postcard/upload `POST`
> <font color="orange">需要带openid的headers</font>  
标准的html上传，可参考www.dutbit.com/home下的上传，如果不正常工作直接看本目录下templates文件夹里的upload.html  
成功返回{success:1,data:上传成功}

- /postcard/【template/audio/image】/【id】（card的id）`GET`
<font color="orange">，错误会直接报HTML状态码500，404，错误详情直接出现在body里面</font>
> image：后面带url参数？size=small/large,返回id相应图片  
> audio: 直接给文件  
> template: <font color="orange">必须带target参数，`target=image||target=audio`  
可选size参数【small||large】，默认small</font>  