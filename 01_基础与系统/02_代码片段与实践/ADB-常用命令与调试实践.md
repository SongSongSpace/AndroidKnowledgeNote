#状态/未完成 #技术栈/ADB #场景/Android调试

#### 1、端口转发

**反向端口转发** **reverse** `adb reverse` 把连接从 Android 设备反向转发到运行 adb 的电脑。

``` adb
adb reverse tcp:7686 tcp:7686
```

