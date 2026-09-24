#状态/未完成 #技术栈/ADB #场景/Android调试

### 一、端口转发

#### 1、反向端口转发

**reverse** `adb reverse` 把连接从 Android 设备反向转发到运行 adb 的电脑。

``` adb
adb reverse tcp:7686 tcp:7686
```

第一个 tcp:7686 设备端要监听的 TCP 端口。

第二个 tcp:7686 电脑端要转发的 TCP 端口。

==当手机/模拟器里的应用访问 localhost:7886 时，实际访问的是你电脑上监听 7686 端口的服务。

#### 2、正向端口转发

**forward** `adb forward` 