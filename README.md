# ha-wework_notify
HomeAssistant 企业微信推送

修改自： \
https://bbs.hassbian.com/thread-16924-1-1.html \
https://bbs.hassbian.com/thread-12547-1-1.html \
https://bbs.hassbian.com/thread-7128-1-1.html 

jijngpengboo 和 27hh 版本基础再修改的版本...

## 修改
（主要针对news类型消息） \
1、同时支持本地上传图片和网络地址的图片，增加 target 微信接收者。 \
2、优先使用imagepath上传本地图片，如果 imagepath 本地址图片不存在或未填写时使用 picurl 网络地址。 \
  如果 picurl 网络地址也未配置，则发送无图片带标题的链接卡片(与原来的一致) \
3、url 不填写则使用图片的链接

## 安装

* 将 custom_component 文件夹中的内容拷贝至自己的相应目录

或者
* 将此 repo ([https://github.com/dscao/ha-wework_notify](https://github.com/nesror/ha-wework_notify)) 添加到 [HACS](https://hacs.xyz/)，然后添加“Wework Notify”

## 配置
```yaml
notify:
  - platform: wework_notify
    name: wework          # 实体ID  比如这个出来就是notify.wework
    corpid:               # 这个是企业微信的企业id
    agentId: "1000002"    # 这个是企业微信里面新建应用的应用id
    secret:               # 这个是企业微信里面新建应用的应用secret
    touser: '@all'        # 默认接收者， @all为全体成员，也可用具体ID： 如：userid1|userid2|userid3
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
  message: 发送带标题、内容和头图的链接卡片  
  title: 推送视频
  data:
    type: video
    videopath: /config/www/1.mp4

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

