## 目录

1. Binder 进程间通信机制
2. SystemServer 进程
3. Zygote 进程
4. Init 进程
5. ActivityManagerService
6. Activity 生命周期分析
7. 关键系统进程启动流程
8. Launcher 请求 AMS/ATMS 与 Activity 启动流程
---
# 一、Binder 进程间通信机制

## 1. IPC 机制概览

Android 中常见的进程间通信机制包括：
- Binder
- 管道
- Socket

在基于 Binder 通信的 C/S 架构体系中，除了：
- Client 端
- Server 端

还有一个全局的 **ServiceManager 端**。
> 一个 Server 进程可以注册多个 Service。

## 2. MediaServer

**MediaServer（MS）** 是以下重要 Service 的栖息地：
- AudioFlinger
- AudioPolicyService
- MediaPlayerService
- CameraService
## 3. ProcessState

|特性|说明|
|---|---|
|数量|每个进程只有一个 ProcessState|
|设计模式|单例模式|
|构造函数|会打开 Binder 设备|
|核心函数|`open_driver()`：打开 `/dev/binder`|
|设备性质|`/dev/binder` 是 Android 在内核中为完成 IPC 专门设置的虚拟设备|

`ProcessState` 的实现要点：
1. 打开 Binder 设备，与内核 Binder 驱动建立交互通道。
2. 对返回的 fd 使用 `mmap`，由 Binder 驱动分配一块内存接收数据。
3. 一个进程只打开设备一次，因为一个进程只有一个 `ProcessState`。
## 4. defaultServiceManager

- 函数实现在 `IServiceManager.cpp` 中。
- 返回一个 `IServiceManager` 对象。
- 通过该对象，可以与另一个 **ServiceManager 进程** 进行交互。
- 返回对象是调用 `ProcessState` 的 `getContextObject` 函数得到的。

调用链：
```cpp
gDefaultServiceManager = interface_cast<IServiceManager>(
    ProcessState::self()->getContextObject(NULL)
);
```

进一步：
```text
getContextObject -> getStrongProxyForHandle -> 返回 BpBinder(handle)
```

## 5. BpBinder 与 BBinder

| 类型                | 角色          | 说明                                                  |
| ----------------- | ----------- | --------------------------------------------------- |
| `BpBinder`        | 客户端代理类      | `p` 即 Proxy；用于与 Server 交互                           |
| `BBinder`         | 目的端         | proxy 交互的相对端                                        |
| 对应关系              | 一一对应        | `BpBinder` 通过 `handle` 标识对应的 `BBinder`              |
| ServiceManager 场景 | handle 值为 0 | 因为它是 ServiceManager 的客户端，所以使用代理端与 ServiceManager 交互 |
| 与 Binder 设备关系     | 不直接交互       | `BBinder` / `BpBinder` 没有和 Binder 设备直接交互            |

`BpBinder` 是 `defaultServiceManager` 的“道具”。
## 6. interface_cast 与 IServiceManager

- `interface_cast`：模板函数，将 `BpBinder` 指针转换成 `IServiceManager` 对象并返回。
- 它利用 `BpBinder` 对象作为参数新建一个 `BpServiceManager` 对象，其 `mRemote` 值是 `BpBinder`。
- `IServiceManager` 的业务函数由 `BpServiceManager` 对象实现。
## 7. 注册 MediaPlayerService

### 7.1 业务层工作

调用路径：
```text
defaultServiceManager() -> addService -> transact()
```

要点：
- 注册服务时，实现 `defaultServiceManager()`、`addService()`。
- `addService()` 返回 `IServiceManager`，实际是 `BpServiceManager`。
- `addService()` 中：
    - `Parcel data, reply;`
    - `remote()->transact()` 会返回 `BpBinder` 对象。
- `addService` 中把请求数据打包成 `data` 后，传给 `BpBinder` 的 `transact` 函数，即把通信工作交给 `BpBinder`。
- 本质：将请求信息打包后，交给通信层处理。
### 7.2 通信层工作：IPCThreadState

- `BpBinder` 把 `transact` 工作交给 `IPCThreadState#transact()`。

**TLS：Thread Local Storage，线程本地存储空间**
- 每个线程都有这种空间。
- 线程间不共享。
- 通过 `pthread_getspecific` / `pthread_setspecific` 获取或设置空间中的内容。

`IPCThreadState` 中：

|成员|作用|
|---|---|
|`mIn`|接收来自 Binder 设备的数据|
|`mOut`|存储发往 Binder 设备的数据|
|类型|`Parcel`，可看作发送和接收命令的缓冲区|

消息码约定：
- 应用程序向 Binder 设备发送消息的消息码以 `BC_` 开头。
- 反过来以 `BR_` 开头。

流程：
```text
先发数据：writeTransactionData()
再等结果：waitForResponse() -> talkWithDriver()
处理：executeCommand()
talkWithDriver()：与 Binder 设备交互
```

## 8. StartThreadPool 与 joinThreadPool

启动线程池调用链：
```text
StartThreadPool -> spawnPooledThread(true) -> new PoolThread(true) -> joinThreadPool(true)
```

`joinThreadPool` 要点：
- 请求信息写到 `mOut` 中，等会儿一起发出去。
- 处理死亡的 `BBinder` 对象。
- 发送命令读取请求：`talkWithDriver()`。
---

# 二、SystemServer 进程

## 1. 作用

SystemServer 用于创建系统服务，例如：
- AMS
- ATMS
- WNS
- PMS

其进程名为：
```text
system_server
```

主要工作：

1. 启动 Binder 线程池，用于与其他进程进行 Binder 通信。
2. 创建 `SystemServiceManager`，用于启动、创建和管理服务。
3. 启动各种系统服务，分为：
    - 引导服务
    - 核心服务
    - 其他服务
## 2. ZygoteInit#zygoteInit 参数
```java
ZygoteInit#zygoteInit(
    int targetSdkVersion,
    long[] disableCompatChanges,
    String[] args,
    ClassLoader classLoader
)
```

|参数|说明|
|---|---|
|`targetSdkVersion`|系统设置的目标 SDK 版本|
|`disabledCompatChanges`|禁用的一些兼容选项|
|`argv`|传递给虚拟机的启动参数，也就是 `main` 方法接收到的参数|
## 3. 启动 Binder 线程池

调用链：
```text
ZygoteInit.nativeZygoteInit()
    -> ProcessState#startThreadPool
    -> 启动 Binder 线程池
```

## 4. 设置虚拟机的 TargetSDKVersion

```text
RuntimeInit#applicationInit
    -> 根据传入参数启动 Java Main 方法
    -> findStaticMain()
    -> 使用反射创建入口类
```

## 5. SystemServer#main
```java
public static void main(String[] args) {
    new SystemServer().run();
}
```

`run()` 主要步骤：

|序号|工作|
|---|---|
|1|设置 Binder 线程池最大线程数，Android 10 中为 31|
|2|设置当前进程优先级|
|3|创建 SystemServer 进程的主线程 Looper|
|4|允许堆内存分析|
|5|创建系统上下文|
|6|创建系统管理服务|
|7|启动引导服务：`startBootstrapServices(t)`|
|8|启动核心服务：`startCoreServices(t)`|
|9|启动其他服务：`startOtherServices(t)`|
|10|开启 Loop 循环|

## 6. ActivityTaskManagerService 服务启动流程
- 创建 `SystemServiceManager`，由它负责创建、启动和管理服务。
- `SystemServiceManager#startService`：注册服务、调用 `onStart()`。
- `ActivityTaskManagerService.Lifecycle#onStart`：
    1. 将 `ActivityTaskManagerService` 对象注册到 `ServiceManager` 中，其他进程通过访问 `ServiceManager` 获取 ATMS 的代理对象。
    2. 将 `ActivityTaskManagerService` 的内部类 `LocalService` 添加到本地服务列表。`LocalService` 不是一个 `IBinder` 对象，它用于当前进程内部使用 ATMS 服务。
---

# 三、Zygote 进程
> 原文此处有 `strcmp()` 小标题，但未展开内容。

## 1. init.zygote64_32.rc
`init.zygote64_32.rc` 文件包含两个 `service` 指令，对应两个 Zygote 进程。
入口函数位于：
```text
frameworks/base/cmds/app_process/app_main.cpp
```

## 2. 两个 Zygote 进程

### 进程 1：Zygote 进程
- 通过 `/system/bin/app_process64` 启动。
- 会创建一个名为 `zygote` 的 socket。
- 通过执行 `/system/bin/app_process64` 并传入参数启动 Zygote 进程。

参数如下（原文写“4 个参数”，实际列出 5 项）：

|参数|说明|
|---|---|
|`-Xzygote`|作为虚拟机启动时所需的参数|
|`/system/bin`|代表虚拟机程序所在目录|
|`--zygote`|指明以 `ZygoteInit.java` 类中的 `main` 函数作为虚拟机执行入口|
|`--start-system-server`|告诉 Zygote 进程启动 SystemServer 进程|
|`--socket-name`|指定 socket 的名字|

### 进程 2：Zygote_secondary 进程

- 通过 `/system/bin/app_process32` 启动。
- 会创建一个名为 `zygote_secondary` 的 socket。
## 3. Zygote 进程入口函数

流程如下：
1. `frameworks/base/cmds/app_process/app_main.cpp`：创建 `AppRuntime` 对象。
2. 根据传入参数判断当前进程类型：
    - Zygote
    - 应用进程  
        不同进程开启不同的 `runtime.start()`：
    - Zygote 启动，加载 `ZygoteInit`
    - Application 启动模式，加载 `RuntimeInit`
3. `AppRuntime#start`
4. 继承自 `AndroidRuntime#start()`
5. 初始化 JNI 服务，创建启动 Dalvik 虚拟机。
6. 根据传入的 `className`，使用 JNI 调用 `ZygoteInit#static void main(String[] args)` 方法。
7. `ZygoteInit#main`
8. 预加载类和资源，子进程无需再加载。
9. 使用大量 systrace 监控方法执行性能。
10. 加载 Android 中的一些关键类：
    - 公共资源
    - 硬件抽象层
    - 图形驱动
    - 公共类库
    - 公用文字资源
    - WebView
    - 用于 hook 的函数等
11. 这些预加载类定义在：
```text
    frameworks/base/config/preloaded-classes
```
    Android 10 中一共有 1 万多个。  
    资源主要是加载 `framework-res.apk` 中的资源、OpenGL、WebView 等。常用的 `android.R` 文件就来自这里。
12. 创建服务端 Socket，用于与其他进程通信。
13. 启动 SystemServer 进程。
14. 首次启动时会通过 `fork` 自身的方式启动 SystemServer 进程，然后等待子进程 Socket 请求，通过 `fork Zygote` 快速创建一个已经初始化好的“Java 世界”。
15. 代码片段：
```java
    Runnable r = forkSystemServer(abList, zygoteSocketName, zygoteServer);
    if (r != null) r.run();
```
16. 子进程调用 `handleSystemServerProcess` 方法，返回 `Runnable` 对象。
17. 开启循环，等待客户端请求：`ZygoteServer#runSelectLoop`
18. 无限等待，等待 SystemServer 通知它创建进程。
19. 利用管道机制阻塞等待事件。
20. 优先处理已建立链接的事件，后处理新建链接的请求。
## 4. Zygote 主要工作流程

1. 启动 Android 系统中第一个 Java 虚拟机，并初始化 JNI，注册 Android 中的 JNI 函数。
2. 调用 Java 层 `ZygoteInit` 类的 `main` 函数，进入 Java 世界。
3. 建立 Socket 服务端，用于与客户端进行 IPC 通信，主要是接收 SystemServer 的启动 App 进程请求。
4. 预加载类、资源、WebView 等。
5. 通过 `fork` 自身的方式，启动 SystemServer 进程。
6. 调用 `runSelectLoopMode` 方法，进入无限循环，等待创建子进程的请求。
---

# 四、Init 进程

## 1. Android 系统启动过程

|阶段|说明|
|---|---|
|1. 启动电源及系统|电源按下时，引导芯片代码从预定义地方（固化在 ROM）开始执行。加载引导程序 BootLoader 到 RAM 中，然后执行|
|2. 引导程序 BootLoader|Android 操作系统开始运行前的一个小程序，主要作用是把系统 OS 拉起来并运行|
|3. Linux Kernel 启动|内核启动时，设置缓存、被保护存储器、计划列表、加载驱动。内核完成系统设置后，首先在系统文件中寻找 `init.rc` 文件，并启动 init 进程|
|4. Init 进程启动|init 进程工作较多，主要用来初始化和启动属性服务，也用来启动 Zygote 进程|
## 2. Init 进程入口函数

入口为 `main()` 方法。
主要分支：

|分支|作用|
|---|---|
|`ueventd`|设备节点创建、权限设定|
|`Subcontext`|初始化日志系统|
|`selinux_setup`|启动 SELinux 安全策略|
|`second_stage`|第二阶段：`SecondStageMain(argc, argv)`|
|第一阶段|`FirstStageMain(argc, argv)`|

## 3. 第一阶段

- `ueventd` / `watchdogd` 跳转
- 环境变量设置
- init crash 时重启引导加载程序
- 初始化日志输出
- 创建挂载相关文件目录
- 传入 `selinux_setup` 到 `main.cpp`，启用 SELinux 安全策略
- 初始化内核 log 系统
## 4. 第二阶段

- 创建进程会话密钥：创建和启动 `service` 命令指定的进程
- 初始化内核 Logging
- 初始化属性服务
- 为第二阶段设置安全策略，执行 SELinux 第二阶段并恢复一些文件安全上下文
- 新建 `epoll` 并初始化子进程终止信号处理函数
- 装载子进程信号处理，防止僵尸子进程无法回收
- 设置其他系统属性并开启属性服务
- 加载解析 `init.rc` 脚本，启动 Zygote 进程和其他进程
## 5. init.rc 文件

- 通过 `import` 导入对应的 Zygote 的 rc 文件。
- 主流厂商使用的是：
```text
    init.zygote64_32.rc
```
---

# 五、ActivityManagerService

## 1. 是什么？

`ActivityManagerService` 是 Android 中最核心的服务，负责系统中四大组件的启动、切换、调度及应用进程的管理和调度等工作。

## 2. 分析
1. Android 系统服务在 SystemServer 进程创建后，通过其 `run()` 方法来启动各类服务。
2. AMS 在 SystemServer 中的 `startBootstrapServices` 方法中启动。
---

# 六、Activity 生命周期分析

生命周期管理相关代码放在 `ActivityTaskManager` 中。
## 1. Attach：绑定数据

Activity 被创建后，首先调用其 `attach` 方法，将一些数据与 Activity 进行绑定。

要点：
- 是 `final` 方法。
- 为 `FragmentManager` 绑定 Controller：
```java
    mFragments.attachHost(/* params */);
```
- 创建 Window：
```java
    mWindow = new PhoneWindow(this, window, activityConfigCallback);
```
- 初始化 Window：
    - `setWindowControllerCallback`
    - `setCallback`
    - `setOnWindowDismissedCallback`
    - `getLayoutInflater()`
    - `setPrivateFactory()`
    - `setSoftInputMode`
    - `setUiOptions()`
- 初始化一系列变量。
- 为 Window 绑定 WindowManager。
## 2. Create 阶段

执行完 `attach` 之后，`ActivityThread` 将会调用 `Instrumentation` 中的 `callActivityOnCreate` 方法开启 Activity 的 Create 阶段。

三个步骤：
1. **预处理**
    - `Instrumentation#prePerformCreate`
    - 将同步启动的 Activity 从列表 `mWaitingActivities` 中移除。
    - 过程包括：上锁、阻塞、等待、解除阻塞。
2. **回调 Activity 的 onCreate() 方法**
    - `Activity#performCreate`
    - 回调、通知 `FragmentManager` 分发 `onActivityCreated` 事件、调用 `ActivityLifecycleCallback` 方法。
    - `Activity#onCreate`：
        - 对于异常重启的 Activity 恢复一些数据。
        - 调用 `dispatchActivityCreated` 来回调所有的 `ActivityLifecycleCallback`。
3. **收尾工作**
    - `Instrumentation#postPerformCreate`
    - 保证 Activity 从列表 `mWaitingActivities` 中移除。
## 3. Start 阶段

目标状态：`ON_RESUME`。
顺序执行 Activity 的生命周期回调：`onStart` 和 `onResume`。
相关组件：
- `TransactionExecutor`
- `cycleToPath()`
- 一个路径的数组
- `performLifecycleSequence()`
- `ClientTransactionHandler`

流程：
```text
ClientTransactionHandler.handleStartActivity()
    -> 回调 Activity#onStart()
    -> performStart()
    -> 恢复数据、调用 Activity 的 onPostCreate 方法
```

`Activity#performStart`：
- 分发 `preStart` 事件
- 调用 `onStart`
- 分发 `postStart` 事件
## 4. Resume 阶段
目标状态：`ON_RESUME`。
继续执行 `handleResumeActivity` 方法。
判断 Activity 的 Window 是否已经添加到 WindowManager 中，是否真正需要显示。
调用链：
```text
WindowManagerImpl#addView
    -> WindowManagerGlobal#addView
    -> ViewRootImpl#setView
    -> 调用 WindowSession 中的 addToDisplay 方法
    -> 将 Window 与 WindowManagerService 绑定
```

Activity 的 Window 显示过程，包括 View 树的绘制过程，都是在 Activity 的 `ON_RESUME` 阶段完成的。

> 所以在 `onCreate`、`onStart` 和 `onResume` 中都无法同步获取到 View 的宽高。

## 5. Pause 阶段

执行 `ActivityThread` 中的 `handlePauseActivity` 方法。
触发原因：
- 用户导致，如按下 back 键、home 键、点击跳转等。
调用：
- `Activity#onUserInteraction`
- `Activity#onUserLeaveHint`
- `onSaveInstanceState`

`Activity#performPause`：
- 分发 `prePause`、`onPause` 和 `postPause` 事件。
## 6. Stop 阶段

调用 `handleStopActivity`。
要点：
- stop 后隐藏 Activity 的 `DecorView` 显示。
- 保证 Activity 是处于 Pause 状态。
### onSaveInstanceState 调用时机

|版本阶段|调用时机|
|---|---|
|Android Honeycomb 之前|`onSaveInstanceState` 在 `onPause` 调用之前被调用|
|Android Honeycomb 之后，Android P 之前|`onSaveInstanceState` 在 `onStop` 调用之前被调用|
|Android P 之后|`onSaveInstanceState` 在 `onStop` 调用之后被调用|

`Activity#onStop()` 方法：
- 停止 UI 的刷新
- 停止运行中的动画
- 隐藏填充
## 7. Destroy 阶段

完成 Activity 本身的销毁逻辑、通知 System Server 处理 Activity 栈相关的逻辑。

执行：
```text
ActivityThread#handleDestroyActivity
    -> performDestroyActivity
    -> 执行本地的销毁逻辑 + 通知 ATMS 更新系统服务

```
`Instrumentation.callActivityOnDestroy` 会回调 Activity 的 `performDestroy` 方法。

与之前的生命周期类似，`performDestroy` 主要：
- 分发 `preDestroy`、`destroy` 和 `postDestroy` 事件。
- 调用 `onDestroy` 生命周期回调。

`onDestroy` 方法中主要是保证 Activity 销毁时已经关闭了所有的由此 Activity 管理的：
- Dialog
- Cursor
- SearchDialog

这样可以避免一些内存泄漏。
## 8. 非生命周期关键方法分析
### 1. onSaveInstanceState — 保存实例状态
调用：`callActivityOnSaveInstanceState`
调用时机：

|版本阶段|调用时机|
|---|---|
|Android Honeycomb（11）之前|`callActivityOnSaveInstanceState` 在 `onPause` 调用之前被调用|
|Android Honeycomb（11）之后，Android P 之前|`callActivityOnSaveInstanceState` 在 `onStop` 调用之前被调用|
|Android P 之后|`callActivityOnSaveInstanceState` 在 `onStop` 调用之后被调用|

### 2. onRestoreInstanceState — 恢复数据
用于恢复数据。
### 3. retainNonConfigurationInstances
用于保留非配置实例。
---

# 七、关键系统进程启动流程

## 1. 关键进程

|进程|说明|
|---|---|
|init 进程|Linux/Android 系统用户空间的第一个进程，进程号 pid 为 1|
|Zygote 进程|Java 世界的开创者|
|property service|init 提供，用于管理 Android 系统的属性|
init 负责创建系统中的几个关键进程。
## 2. Code analysis

关键代码分析点：
- 设置子进程退出的信号处理函数。
- 创建一些文件夹，并挂载设备。
- 设置 init 的日志输出设备。
- 解析 `init.rc` 配置文件。
- 获得机器的硬件名：
```text
    get_hardware_name()
```
    对应一个机器相关的配置文件，解析它。
    
- Init 将动作 Action 执行的时间划分为四个阶段：
    - `early-init`
    - `init`
    - `early-boot`
    - `boot`
    划分原因：有些动作必须在其他动作完成后才能执行。

## 3. 开机画面

```text
load_565rle_image(INIT_IMAGE_FILE)
```

失败时输出 “ANDROID” 字样。

---

# 八、Launcher 请求 AMS/ATMS 与 Activity 启动流程

## 1. Launcher 请求 AMS 过程

`Launcher.startActivitySafely()`

`startActivitySafely` 中：

- 通过设置 `FLAG_ACTIVITY_NEW_TASK` flag 让 Activity 在新的任务栈中启动。
- 代码：
```java
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
```

## 2. Activity 启动流程

### 2.1 Activity 类型

- App 的 Root Activity
- 普通的 Activity

根 Activity 的启动过程：
1. Launcher 请求 ATMS 过程
2. ATMS 调用 ApplicationThread 过程
3. ActivityThread 启动 Activity 过程
### 2.2 核心类与职责

|类|作用|
|---|---|
|`ActivityThread`|管理应用程序进程的主线程的执行；执行 ATMS 的调度；执行 Activity、Broadcast 及相关操作|
|`ApplicationThread`|`ActivityThread` 的内部类，`ActivityThread` 通过它进行 IPC 调用，与 SystemServer 通信|
|`Instrumentation`|监控应用程序与系统交互；处理启动 Activity 或者调用 Activity、Application 的生命周期|
|`ActivityTaskManagerService`|管理 Activity 和它的回退栈、任务栈的系统服务|
|`ActivityRecord`|system_server 进程中用来描述 Activity 的数据类型。存储 Activity 信息，如所在进程名称、应用包名、所在任务栈的 `taskAffinity` 等|
|`ActivityClientRecord`|App 进程中用来描述 Activity 的数据类型|
|`TaskRecord`|表示一个任务栈，记录 Activity 启动的先后顺序|
|`ActivityStack`|负责维护 `TaskRecord`，内部保存当前 Stack 中所有的 Task 列表|
|`ActivityDisplay`|管理所有 `ActivityStack`|
|`RootActivityContainer`|作为 Activity 容器的根节点，负责管理所有的 `ActivityDisplay`|
|`ActivityStackSupervisor`|Android 系统中 Activity 的最大管家，持有 `RootActivityContainer` 来间接管理所有的 Activity|
|`ClientLifecycleManager`|组合多个客户端生命周期转换和请求，作为单个事务来执行|
|`ActivityStarter`|加载 Activity 的控制类，收集所有逻辑来判断如何将 Intent 和 Flags 转换为 Activity，并将 Activity 和 Task 以及 Stack 相关联|

## 3. 阶段 1：Launcher 请求 ATMS 过程

调用链：

```text
Launcher#startActivitySafely
    ===> Activity#startActivity
    -> startActivity
    ===> Instrumentation#execStartActivity
    ====> 使用 Binder IPC 调用 ActivityTaskManagerService，去启动 Activity
```

## 4. 阶段 2：ATMS 调用 ApplicationThread 过程

主要工作：

1. 判断权限信息，具备权限的调用进程才可以启动 Activity。
2. `ActivityStarter` 解析 Intent 的内容，创建对应的 `ActivityRecord` 对象。
3. 根据是否需要新建 TASK，来新建或者选择对应的 `TaskRecord` 添加 Activity。
4. 处理 Task 相关状态信息，例如前台的转移。
5. 使前台 TASK 的栈顶 Activity 可见，这个过程会启动对应的 Activity，必要情况会启动对应的进程。
6. 通过 IPC 调用将启动 Activity 的事务发送到对应进程中，交由对应的 App 来处理。

## 5. 阶段 3：ActivityThread 启动 Activity 过程

> 附件原文在此处中断，仅保留标题“3 —”，未展开后续内容。