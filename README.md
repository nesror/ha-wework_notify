# HomeAssistant 企业微信推送
[![version](https://img.shields.io/github/manifest-json/v/nesror/ha-wework_notify?filename=custom_components%2Fwework_notify%2Fmanifest.json)](https://github.com/nesror/ha-wework_notify/releases/latest)
[![stars](https://img.shields.io/github/stars/nesror/ha-wework_notify)](https://github.com/nesror/ha-wework_notify/stargazers)
[![issues](https://img.shields.io/github/issues/nesror/ha-wework_notify)](https://github.com/nesror/ha-wework_notify/issues)
[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)
![visit](https://visitor-badge.glitch.me/badge?page_id=nesror.ha-wework_notify&left_text=visit)

### 公众号
关注公众号及时获取最新版，各种使用技巧以及Hass的新奇玩法

<img src="gzh.png" height="120"/>

修改自： \
https://bbs.hassbian.com/thread-16924-1-1.html \
https://bbs.hassbian.com/thread-12547-1-1.html \
https://bbs.hassbian.com/thread-7128-1-1.html

企业微信官方相关文档： \
https://open.work.weixin.qq.com/help2/pc/15381 \
https://developer.work.weixin.qq.com/document/path/90236

jijngpengboo 和 27hh 版本基础再修改的版本...

## 修改
（主要针对news类型消息） \
1、同时支持本地上传图片和网络地址的图片 \
优先使用imagepath上传本地图片，如果 imagepath 本地址图片不存在或未填写时使用 picurl 网络地址。 \
  如果 picurl 网络地址也未配置，则发送无图片带标题的链接卡片(与原来的一致) \
url 不填写则使用图片的链接 \
2、增加 target 微信接收者。 \
3、同时支持news和mpnews类型，mpnews类型时，必须为本地图片上传。可使用safe: 1 为保密消息。 \
4、支持代理服务器设置（暂无有效代理服务器，未测试） \
5、支持接口中转服务器设置（node-red已测试）

## 安装

* 将 custom_component 文件夹中的内容拷贝至自己的相应目录

或者
* 将此 repo ([https://github.com/nesror/ha-wework_notify](https://github.com/nesror/ha-wework_notify)) 添加到 [HACS](https://hacs.xyz/)，然后添加“Wework Notify”

## 配置
```yaml
notify:
  - platform: wework_notify
    name: wework          # 实体ID  比如这个出来就是notify.wework
    corpid:               # 这个是企业微信的企业id
    agentId: "1000002"    # 这个是企业微信里面新建应用的应用id
    secret:               # 这个是企业微信里面新建应用的应用secret
    touser: '@all'        # 默认接收者， @all为全体成员，也可用具体ID： 如：userid1|userid2|userid3
    https_proxies: username:password@XXX.XXX.XXX.XXX:8080   #支持https的代理服务器地址（可选项）
    resource: http://XXX.XXX.XXX.XXX:1880/endpoint   #选配服务器中转地址（可选项），默认为： https://qyapi.weixin.qq.com/cgi-bin ,可设置为 http:xxx.xxx.com:1880/endpoint 或 http:xxx.xxx.com:1880（具体根据node-red的设置）
    resource_username: username  #选配服务器中转基本认证用户 如 node-red中的http_node username （可选项）
    resource_password: password  #选配服务器中转地址认证密码 如 node-red中的http_node password （可选项）
```

## 使用
```yaml
service: notify.wework  #调用服务
data:
  message: 消息内容
  target: 接收者ID1|接收者ID2|接收者ID3

service: notify.wework  #调用服务
data:
  message: 消息内容
  target:
    - 接收者ID1
    - 接收者ID2
    - 接收者ID3


service: notify.wework
data:
  message: 发送纯文本消息，当前时间：{{now().strftime('%Y-%m-%d %H:%M:%S')}}


service: notify.wework
data:
  message: 发送带标题和分隔线的纯文本消息
  title: 这是标题


service: notify.wework
data:
  message: ''
  title: 发送带标题的链接卡片
  data:
    type: news
    url: 'http://www.sogou.com'
   
   
service: notify.wework
data:
  message: 发送带标题和内容的链接卡片
  title: 这是标题
  data:
    type: textcard
    url: 'http://www.sogou.com'
   
   
service: notify.wework
data:
  message: 发送带标题、内容和头图的链接卡片，优先使用上传本地图片，本地址图片不存在时或未配置时使用 picurl网络地址
  title: 这是标题
  data:
    type: news
    url: 'http://www.sogou.com'
    picurl: 'https://bbs.hassbian.com/static/image/common/logo.png'
    imagepath: /config/www/1.jpg   

service: notify.wework
data:
  message: 发送带标题、内容和头图的链接卡片，上传本地图片，mpnews消息与news消息类似，不同的是图文消息内容存储在微信后台，并且支持保密选项（safe: 1，不填写默认为0）。每个应用每天最多可以发送100次。
  title: 这是标题
  data:
    type: mpnews
    url: 'http://www.sogou.com'
    imagepath: /config/www/1.jpg
  safe: 1

service: notify.wework
data:
  message: 发送带标题、内容和头图的链接卡片  
  title: 推送视频
  data:
    type: video
    videopath: /config/www/1.mp4
  safe: 0

```

## 示例
```yaml   
service: notify.wechat
data:
  title: 小汽车当前位置：{{states('sensor.mycar_loc')}}
  message: "状态刷新时间：{{state_attr('device_tracker.gddr_gooddriver',
    'querytime')}}{{'\r\n'}}车辆状态：{{state_attr('device_tracker.gddr_gooddriver',
    'status')}}{{'\r\n'}}到达位置时间：{{state_attr('device_tracker.gddr_gooddriver',
    'updatetime')}}{{'\r\n'}}停车时长：{{state_attr('device_tracker.gddr_gooddriver',
    'parking_time')}}{{'\r\n'}}当前速度：{{state_attr('device_tracker.gddr_gooddriver',
    'speed') | round(1) }}km/h"
  data:
    type: news
    url: "https://uri.amap.com/marker?position={{state_attr('device_tracker.gddr_gooddriver',
      'longitude')+0.00555}},{{state_attr('device_tracker.gddr_gooddriver',
      'latitude')-0.00240}}"
    picurl: "https://restapi.amap.com/v3/staticmap?zoom=14&size=1024*512&markers=large,,A:{{state_attr('device_tracker.gddr_gooddriver',
      'longitude')+0.00555}},{{state_attr('device_tracker.gddr_gooddriver',
      'latitude')-0.00240}}&key=819cxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

```



