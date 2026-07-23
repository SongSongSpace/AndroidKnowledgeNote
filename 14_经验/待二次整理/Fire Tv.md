
**Fire tv cast** **功能文档**

**提供了什么能力？**
- 将媒体内容和手机屏幕投射到 Fire TV 设备上的能力。

**向用户开放哪些行为？**
- 用户可以将手机中的视频、照片、音乐，以及网页视频，无缝地在电视大屏幕上播放。
- 支持将整个手机屏幕实时镜像到电视上。  
**Fire tv cast** **技术文档**
**架构**
- 手机端 SDK + 电视端 Receiver App 的架构。
**设备发现**
- com.amazon.whisperplay.fling.media.controller.DiscoveryController.start()发现设备。
- Amazon Fling发现设备
- 获取设置安装installSerivce属性信息。
- FireOSDeviceModelManager通过 SSDP 搜索发现设备。 

**通信协议**

- HTTP 控制指令。

"https://${ip}:8080/v1/FireTV?action=${it}"

- WebSocket 状态同步。
- Socket 实时推送数据流（镜像）。

  

**初始化连接**

- 使用专用HandlerThread(“name”)来处理所有网络和耗时操作，启动它。
- MutableLiveData运用switchMap构建异步、链式的请求处理流程。

- 各项命令使用单独的liveData，构建不同的switchMap。

- 开始播放，则建立状态监听。

- 通过建立WebSocket，接收电视端播放器实时状态更新。

  

**准备**

- 接受端状态检查（无论镜像还是投屏，这都是具体行为的前置步骤！）

- 是否安装和是否版本符合
- 是否在线（是否启动应用）

- Socket 尝试连接预设端口
- 在线进入下一步，不在线则启动
- 启动：基于目标设备ip和目标应用id，通过api("https://${ip}:8080/v1/FireTV/app/$appId")发送http请求。

- 记住设备信息，开始具体行为（投屏或镜像）

  

**投屏工作流**

- 生成 URL

- 本地媒体

- 通过本地文件路径/转码后路径，生成带有目标设备 ip的 http url。

- 网站媒体

- 是m3u，直接用其url。
- 带Header的，使用代理服务器转发请求生成网络url。
- 否则，直接用其媒体url。

- 发送指令
- 手机端推url，让电视段根据url自己播视频。

  

投屏 - 需要接收端应用辅助

- 手机端发送投屏指令
- 启动播放投屏的电视端应用
- 将视频url通过http命令发送过去
- 接收端根据接收到的url播放视频

  

**镜像工作流**

- 初始化镜像参数
- 启动镜像
- 发送镜像指令
- 建立数据通道

- HTTP响应中包含videoPort和audioPort。
- 调用PacketSender.connect()，与电视端建立数据传输的连接。

- 启动屏幕录制CaptureManager

- 通过 DataCallback回调编码后的音视频数据。
- 通过PacketSender将数据通过Socket传给电视端。

- 心跳维持。
- 停止镜像。
- 电视端根据手机端推的数据包持续解析播放。

  

镜像

- 得不断推视频流和音频流。
- 接收端得不断解析。

  

  

**关键技术点**

- 设备通信：混用 HTTP 和WebSocket、Socket。
- 响应式编程：LiveData、switchMap构建异步、链式的请求处理流程。
- 后台执行：使用专用的HandlerThread处理所有的网络和耗时操作，避免阻塞主线程。