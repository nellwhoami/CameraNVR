# CameraNVR_v2

CameraNVR_v2 是一款监控视频自动备份到网盘的工具，实现免费云备份，我只用辣鸡百度网盘,所以把阿里的代码部分删除了

# 主要功能

1，视频捕获：通过提供的视频流URL，该程序可以捕获实时视频流。

2，运动检测：使用YOLO3 模型识别人行,还算比较准确吧,目前没发现什么问题

3，视频录制：当程序检测到运动时，会开始录制视频，并将包含运动物体的视频段保存在本地

4，视频上传：根据设置，程序录制的视频上传到指定的网盘





*  执行命令：
 
        nohup python3 CameraNVR.py > nohup.out 2>&1 &



# 常见NVR摄像头码流
国内网络摄像机的端口及RTSP地址
#### 1，海康威视
* 默认IP地址：192.168.1.64/DHCP 用户名admin 密码自己设
* 端口：“HTTP 端口”（默认为 80）、“RTSP 端口”（默认为 554）、“HTTPS 端 口”（默认 443）和“服务端口”（默认 8000），ONVIF端口 80。
* 主码流：rtsp://admin:12345@192.0.0.64:554/h264/ch1/main/av_stream
* 子码流：rtsp://admin:12345@192.0.0.64/mpeg4/ch1/sub/av_stream

#### 2，大华
* 默认IP地址：192.168.1.108 用户名/密码：admin/admin
* 端口：TCP 端口 37777/UDP 端口 37778/http 端口 80/RTSP 端口号默认为 554/HTTPs 443/ONVIF 功能默认为关闭，端口80
* RTSP地址：rtsp://username:password@ip:port/cam/realmonitor?channel=1&subtype=0


#### 3，雄迈/巨峰
* 默认IP地址：192.168.1.10 用户名admin 密码空
* 端口：TCP端口：34567 和 HTTP端口：80，onvif端口是8899
* RTSP地址：rtsp://10.6.3.57:554/user=admin&password=&channel=1&stream=0.sdp?

#### 4，天视通
* 默认IP地址：192.168.0.123 用户名admin 密码123456
* 端口：http端口80 数据端口8091 RTSP端口554 ONVIF端口 80
* RTSP地址：主码流地址:rtsp://192.168.0.123:554/mpeg4
* 子码流地址:rtsp://192.168.0.123:554/mpeg4cif
* 需要入密码的地址： 主码流 rtsp://admin:123456@192.168.0.123:554/mpeg4
* 子码流 rtsp://admin:123456@192.168.0.123:554/mpeg4cif


#### 5，中维/尚维
* 默认IP地址：DHCP 默认用户名admin 默认密码 空
* RTSP地址：rtsp://0.0.0.0:8554/live1.264（次码流）
* rtsp://0.0.0.0:8554/live0.264 (主码流)

#### 6，九安
* RTSP地址：rtsp://IP:port（website port）/ch0_0.264（主码流）
* rtsp://IP:port（website port）/ch0_1.264（子码流）

#### 7，技威/YOOSEE
* 默认IP地址：DHCP 用户名admin 密码123
* RTSP地址：主码流：rtsp://IPadr:554/onvif1
* 次码流：rtsp://IPadr:554/onvif2
* onvif端口是5000
* 设备发现的端口是3702

#### 8，V380
* 默认IP地址：DHCP 用户名admin 密码空/admin
* onvif端口8899
* RTSP地址：主码流rtsp://ip//live/ch00_1
* 子码流rtsp://ip//live/ch00_0

#### 9，宇视
* 默认IP地址： 192.168.0.13/DHCP 默认用户名 admin 和默认密码 123456
* 端口：HTTP 80/RTSP 554/HTTPS 110(443)/onvif端口 80
* RTSP地址：rtsp://用户名:密码@ip:端口号/video123 123对应3个码流

#### 10，天地伟业
* 默认IP地址：192.168.1.2 用户名“Admin”、密码“1111”
* onvif端口号“8080”
* RTSP地址：rtsp：//192.168.1.2

#### 11，巨龙/JVT
* 默认IP地址：192.168.1.88 默认用户名 admin 默认密码admin
* 主码流地址:rtsp://IP地址/av0_0
* 次码流地址:rtsp://IP地址/av0_1
* onvif端口 2000


#### 12，TP-Link/水星安防
* 默认IP地址：192.168.1.4   用户名“Admin”、密码“app里设置”
* 主码流地址:rtsp://user:password@ip:554/stream1
* 次码流地址:rtsp://user:password@ip:554/stream2


# 使用说明
由于能力有限，本源码可能存在缺陷，不保证能用，不要用于商业行为，仅供学习使用！
注意：涉及到有隐私的视频请勿使用本源码，上传到网盘中有可能会造成泄露！

感谢各位大佬的分享的参考源码：

https://github.com/wfxzf/pyNvr

https://github.com/houtianze/bypy

https://github.com/foyoux/aligo

