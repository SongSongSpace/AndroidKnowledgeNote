# RTC 学习与排障

## 建连与采集路径

1. [[概念与机制/RTC/WebRTC基本原理|RTC-基本原理]]：先了解 RTC 组成。
2. [[概念与机制/网络/NAT|网络-NAT]] → [[概念与机制/网络/NAT穿透|网络-NAT穿透 Hole Puching 技术]] → [[概念与机制/连接/P2P连接|架构-P2P 连接]]：理解双方为什么需要发现地址和穿透。
3. [[操作与方案/连接/WebSocket信令与UDP打洞|网络-P2P直连架构（WebSocket信令与UDP打洞）]] → [[概念与机制/RTC/RTC信令与建连流程|RTC-信令与建立连接流程]] → [[概念与机制/RTC/WebRTC SDP|RTC-WebRTC SDP详解]]：区分信令、候选地址与媒体协商。
4. [[概念与机制/RTC/WebRTC媒体采集对象|RTC-WebRTC 媒体采集API]]、[[概念与机制/RTC/WebRTC Android Native API|RTC-Android Native API]]：进入采集对象和 Android API；抓屏另见 [[操作与方案/媒体采集/Android抓屏方案|采集-Android抓屏方案技术总结]]。

## 已有故障经验

- 采集端无声、接收端有刺耳音频：[[故障与复盘/RTC/采集端无声与接收端刺耳音频|WebRTC 采集端“无声”导致接收端刺耳音频——踩坑沉淀]]。这篇讨论数字静音、底噪与增益的可能关系；具体设备结论仍需实测。

原 RTC MOC 中的示例双链并非有效导航；以本页的实际文件链为准。
