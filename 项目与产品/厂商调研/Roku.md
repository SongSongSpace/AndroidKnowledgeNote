**Roku cast** **产品文档**

  

提供了什么能力？

- 将手机内的媒体内容投射到Roku流媒体设备上的能力。

  

用户可以进行哪些行为？

- 用户可以将手机上的照片、视频和音乐，通过 APP 一键发送到电视设备上进行播放。

  

**Roku cast** **技术文档**

架构

- APP SDK + 电视端Receiver应用
- RokuReceiverCOntroller，自定义通信协议的核心。单例。负责与receiver建立底层的、持久化的Socket连接，并发送指令。

  

设备发现

- 基于ConnectSDK 发现设备

  

连接

- 基于ConnectSDK 连接设备。
- 一旦捕获到 CONNECTED 事件，创建一个 RokuCastSession实例，包含ConnectableDevice对象。

  

准备

- 检查安装状态
- 已安装，建立自定义Socket连接。

  

建立自定义Socket连接（m3u格式视频）

- 在后台线程池中，尝试建立 TCP Socket连接。成功，进入下一步。
- 启动两个后台任务。

- startCastCommandThread: 监听一个 LinkedBlockingDeque (指令队列)，循环地从中取出 JSON 指令并写入 castSocket 的输出流。
- startReceiveStateThread: 持续读取 castSocket 的输入流，接收 Roku Receiver 发回的执行结果。

  

发送投屏指令

- 构建包含多个字段的JSONObject。
- 将 JSON 对象放入指令队列。

  

接收指令回执

- startReceiveStateThread读取返回的数据。
- 解析 JSON。

  

播放控制

- 使用设备提供的mediaPlayer媒体播放器播放媒体。
- RokuService提供 PlayMedia能力。

- 区分接收端是不是目标 receiver应用。

- 使用设备提供的mediaControl接口发送标准协议指令。

  

关键技术点

- TCP Socket。自定义通信协议。
- 混合架构