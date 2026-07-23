
**Binder**

  

进程间通信(IPC)机制：Binder \ 管道 \ socket。

  

在基于Binder通信的C/S 架构体系中，除了C/S架构所包括的Clinet端和Sever端以外，还有一个全局的ServiceManager端。

  

  

一个Server进程可以注册多个Service。

  

  

**MediaServer(MS):**

  

是诸如AudioFlinger、AudioPolicyService、MediaPlayerService、CameraService等重要Service的栖息地。

  

1、ProcessState

  

- 每个进程只有一个ProcessSate，独一无二。
- 单例模式。
- ProcessState构造函数打开了Binder设备。

- open_driver()：打开/dev/binder设备，它是Android在内核中为完成进程间通信而专门设置的一个虚拟设备。

- 实现：

- 打开binder设备，与内核的Binder驱动有了交互的通道
- 对返回的fd使用mmap，Binder驱动分配一块内存接收数据
- 一个进程只打开设备一次，由于一个进程只有一个ProcessState

  

2、defaultServiceManager

  

- 函数实现在IServiceManager.cpp中完成
- 函数会返回一个IServiceManager对象，通过这个对象，可以与另一个ServiceManager进程进行交互。
- 函数中返回的对象是调用了ProcessState的getContextObject函数返回的。

- gDefaultServiceManager = interface_cast<IServiceManager>(ProcessState: self() -> getContextObject(NULL))
- getContextObject — > getStrongProxyForHandle() —> 返回BpBinder(handle)

  

- BpBinder：defaultServiceManager的“道具”

- BpBinder和BBinder是Android中与Binder通信相关的，是从IBinder类中派生而来。
- BpBinder是客户端用来与Server交互的代理类，p即Proxy的意思。
- BBinder是proxy相对的一端，是proxy交互的目的端。
- BBinder与BpBinder一一对应，BpBinder通过handler标识对应的BBinder，handle值是0。
- 因为是ServiceManager的客户端，所以使用代理端与ServiceManager进行交互。
- BBinder \ BpBinder没有和binder设备直接交互。

  

- interface_cast：模版函数，将BpBinder指针转换成IServiceManager对象，并返回。

- 利用BpBinder对象作为参数新建一个BpServiceManager对象，它的mRemote值是BpBinder。

  

- IServiceManager：

- BpServiceManager对象实现IServiceManager的业务函数

  

3、注册MediaPlayerService

  

- 业务层的工作 — defaultServiceManager() -> addService -> transact()

- 注册服务，实现defaultServiceManager()函数，addService()，返回IServiceManager，实际是BpServiceManager。
- addService()

- Parcel data ,reply。
- remote() -> transact() -> 会返回BpBinder对象。

- addService中把请求数据打包成data后，传给BpBinder的transact函数，即把通信的工作交给了BpBinder。 — 将请求信息打包后，交给通信层去处理。

  

- 通信层的工作 — IPCThreadState

- BpBinder把transact工作交给了IPCThreadState#transact()

- TLS — Thread Local Storage — 线程本地存储空间的简称

- 这种空间每个线程都有，而且线程间不共享。
- 通过pthread_getspecific/pthread_setspecific函数来获取或设置空间中的内容。

- IPCThreadState中有一个mIn，用来接收来自Binder设备的数据；一个mOut，用来存储发往Binder设备的数据的。它们是Parcel，是看作发送和接收命令的缓冲区。

- 应用程序向binder设备发送消息的消息码以BC_开头，反过来以BR_开头。
- 先发数据 - writeTransactionData()，再等结果 - waitForResponse()  -》 talkWithDriver()。
- 处理  - executeCommand()
- talkWithDriver() — 与binder设备交互。

  

4、StartThreadPool  —> spawnPooledThread(true) —> new PoolThread(true) —> joinThreadPool(true)

  

5、joinThreadPool

- 请求信息写到mOut中，等会儿一起发出去。
- 处理死亡的BBinder对象。
- 发送命令读取请求 — talkWithDriver()。

  

  

  

  

**System Server****进程**

  

用于创建系统服务，如AMS、ATMS、WNS 和 PMS都是由它创建的，其进程名为“system_server”。

  

- 启动Binder线程池，用于与其他进程进行Bind通信

  

- 创建SysytemServiceManager，用于启动、创建和管理服务

  

- 启动各种系统服务，分为引导服务、核心服务和其他服务

  

  

ZygoteInit#zygoteInit(int targetSdkVersion, long[] disableCompatChanges, String[] args, ClassLoader classsLoader) 

1. targetSdkVersion：系统设置的目标SDK版本
2. disabledCompatChanges：禁用的一些兼容选项
3. argv：传递给虚拟机的启动参数，也就是main方法接收到的参数

  

启动Binder线程池:

  

ZygoteInit.nativeZygoteInit(). — > ProcessState#startThreadPool 启动Binder线程池。

  

设置虚拟机的TargetSDKVersion： RuntimeInit#applicationInit —   根据传入参数启动Java Main方法 — findStaticMain():使用反射创建的入口类

  

SystemServer#mian — SystemServer.java

  

public static void main(String[] args) {

    new SystemServer().run();

}

  

run():

1. 设置binder线程池最大线程数，Android 10里为31.
2. 设置当前进程优先级
3. 创建SystemServer进程的主线程Looper
4. 允许堆内存分析。
5. 创建系统上下文
6. 创建系统管理服务
7. 启动引导服务 — startBootstrpServices(t)
8. 启动核心服务 — startCoreService(t)
9. 启动其他服务 — startOtherService(t)
10. 开启Loop循环

  

  

ActivityTaskMannagerService服务启动流程：

创建SystemServiceManager，由它负责创建、启动和管理服务。

  

SystemServiceManager#startService — 注册服务、调用onStart()

  

ActivityTaskService.Lifecycle#onStart — 

1. 将ActivityTaskManagerService对象注册到ServiceManager中，其他进程通过访问ServiceManager来获取ActivityTaskManagerService的代理对象。
2. 将ActivityTaskManagerService的内部类LocalService添加到本地服务列表，LocalService不是一个IBinder对象，它用于当前进程内部使用ATMS服务

  

  

**Zygote****进程**

  

**strcmp()**

  

init.zygote64_32.rc文件包含两个service指令，对应两个Zygote进程，入口函数位于frameworks/base/cmds/app_process/app_main.cpp中。

  

进程1: Zygote进程

  

进程通过/system/bin/app_process64来启动，并且会创建一个名为zygote的socket。

  

通过执行进行/system/bin/app_process64并传入4个参数启动Zygote进程，这五个参数分别是：

1. -Xzygote：该参数将作为虚拟机启动时所需的参数
2. /system/bin：代表虚拟机程序所在目录
3. –zygote：指明以ZygoteInit.java类中的main函数作为虚拟机执行入口
4. –start-system-server：告诉Zygote进程启动systemServe进程
5. –socket-name：指定socket的名字

  

进程2: Zygote_secondary进程

  

进程通过/system/bin/app_process32来启动，并且会创建一个名为zygote_secondary的socket。

  

**Zygote****进程入口函数：**

  

1. frameworks/base/cmds/app_process/app_main.cpp  — 创建AppRuntime对象。
2. 根据传入的参数判断当前进程类型，或为Zygote或为应用进程。不同的进程开启不同的runtime.start()。Zygote启动，加载ZygoteInit；application 启动模式，加载RuntimeInit。
3. AppRuntime#start

4. 继承自AndroidRuntime — #start() — 

5. 初始化JNI服务，创建启动Dalvik虚拟机；
6. 根据传入的className，使用JNI调用ZygoteInit#“static void main(String[] args)"方法。

7. ZygoteInit#main

8. 预加载类和资源 — 子进程就无需再加载

9. 使用大量systrace监控方法执行性能
10. 加载Android中的一些关键类 -- 公共资源、硬件抽象层、图形驱动、公共的类库、公用的文字资源、Webview、用于 hook的函数等
11. 这些预加载的类都是Android中的一些关键类，整个列表定义在frameworks/base/config/preloaded-classes中，Android 10中一共有1万多个。资源主要是加载framework-res.apk中的资源、openGL以及WebView等，我们经常用的android.R文件就是来自这里。

12. 创建服务端Socket — 用于与其他进程通信
13. 启动SystemServer进程

14. 首次启动时会通过fork自身的方式启动SystemServer进程，然后等待子进程Socket请求，通过fork Zygote快速创建一个已经初始化好的"Java 世界“。
15. Runnable r = forkSystemServer(abList, zygoteSocketName, zygoteServer); if(r != null) r.run()
16. 子进程调用handleSystemServerProcess方法，返回Runable对象。

17. 开启循环，等待客户端请求 — ZygoteServer#runSelectLoop

18. 无限等待，等待SystemServer通知它（Zygote）创建进程。
19. 利用管道机制阻塞等待事件。
20. 优先处理已建立链接的事件，后处理新建链接的请求。

21. 主要工作流程：

22. 启动Android系统中第一个Java虚拟机，并且初始化了JNI，注册了Android中的JNI函数。
23. 调用Java层ZygoteInit类的main函数，进入Java世界。
24. 建立Socket服务端，用于与客户端进行IPC通信，主要是接收SystemServer的启动App进程请求。
25. 预加载类、资源、Webview等。
26. 通过fork自身的方式，启动SystemServer进程。
27. 调用runSelectLoopMode方法，进入无限循环，等待创建子进程的请求。

  

  

  

**Init****进程**

  

Android 系统的启动过程：

  

1. 启动电源以及系统系统：当电源按下时引导芯片代码从预定义的地方（固化在 ROM）开始执行。加载引导程序BootLoader到RAM中，然后执行。
2. 引导程序BootLoader：引导程序BootLoader是在Android操作系统开始运行前的一个小程序，它的主要作用是把系统OS拉起来并运行。
3. Linux Kernel启动：当内核启动时，设置缓存、被保护存储器、计划列表、加载驱动。在内核完成系统设置后，它首先在系统文件中寻找init.rc文件，并启动init进程。
4. Init 进程启动：init进程做的工作比较多 ，主要用来初始化和启动属性服务，也用来启动 _Zygote_ 进程。

  

Init进程入口函数：

  

main()方法。

  

1. “ueventd"  — 设备节点创建、权限设定
2. “Subcontext" — 初始化日志系统
3. “selinux_setup" — 启动Selinux安全策略
4. “second_stage" — 第二阶段 — SecondStageMain(argc, argv)
5. 第一阶段 — FirstStageMain(argc, argv)

  

第一阶段：

  

ueventd/watchdogd跳转

环境变量设置

init crash时重启引导加载程序

初始化日志输出

创建挂载相关文件目录

传入selinux_setup 到main.cpp，启用SELinux安全策略

初始化内核log系统

  

第二阶段：

  

创建进程会话密钥 — 创建和启动service 命令指定的进程

初始化内核Logging

初始化属性服务

为第二阶段设置安全策略，执行SELinux第二阶段并恢复一些文件安全上下文

新建epoll并初始化子进程终止信号处理函数

装载子进程信号处理，防止僵尸子进程无法回收

设置其他系统属性并开启属性服务

加载解析init.rc脚本，启动Zygote进程和其他进程

  

  

init.rc文件：

  

通过import导入对应的Zygote的rc文件，主流厂商使用的是init.zygote64_32.rc。

  

  

**ActivityManagerService**

  

一、是什么？

  

Android中最核心的服务，负责系统中四大组件的启动、切换、调度及应用进程的管理和调度等工作。

  

二、分析：

  

1、Android系统服务在SystemServer进程创建后，通过其run()方法来启动各类服务。

  

2、AMS在SystemServer中的startBootstrapServices方法中启动

  

  

  

**Activity****生命周期分析**

  

生命周期管理相关代码放在类ActivityTaskManager中

  

**1****、****Attach****：绑定数据。****Activity****被创建后首先调用其****attach****方法将一些数据与****activity****进行绑定。**

  

final 方法

为FragmentManager绑定Controller — mFragments.attachHost(/*params*/)

创建Window — mWindow = new PhoneWindow(this, window, activityConfigCallback)

初始化Window — setWindowControllerCallback \ setCallback \ setOnWindowDismissedCallback \ getLayoutInflater()

.setPrivateFactory() \ setSoftInputMode \ setUiOptions()

初始化一系列变量

为Window绑定WindowManager

  

**2****、****Create****阶段：执行玩****attach****之后，****ActivityThread****将会调用****Instrumentation****中的****callActivityOnCreate****方法开启****Activity****的****Create****阶段。**

  

三个步骤：预处理、回调创建方法、收尾工作。

  

- 预处理：Instrumentation#prePerformCreate — 将同步启动的Activity从列表mWaitingActivities中移除。（上锁、阻塞、等待、解除阻塞）
- 回调Activity的onCreate()方法：Activity#**performCreate** — 回调、通知FragmentManager分发onActivityCreated事件、调用ActivityLifecycleCallback方法 ==》 Activity#onCreate：对于异常重启的Activity恢复一些数据、调用dispatchActivityCreated来回调所有的ActivityLifecycleCallback。
- 收尾工作：Instrumentation#postPerformCreate — 保证Activity从列表mWaitingActivities中移除。

  

**3****、****Start****阶段：目标状态****ON_RESUME****，顺序执行****Activity****的生命周期回调****onStart****和****onResume****。**

  

TransactionExecutor  \  cycleToPath()  \  一个路径的数组  \ performLifecycleSequence() \ ClientTransactionHandler

  

ClientTransactionHandler.handleStartActivity() — 回调Activity#onStart()方法  — **performStart**()方法 — 恢复数据、调用Activity的onPostCreate方法

  

Activity#performStart — 分发preStart事件、调用onStart、分发postStart事件

  

**4****、****Resume****阶段：目标状态****ON_RESUME****，继续执行****handleResumeActivity****方法。**

  

判断Activity的Window是否已经添加到WindowManager中，是否真正需要显示的。 — WindowManagerImpl#addView —  WindowManagerGlobal#addView —  ViewRootImpl#setView  — 调用WindowSession中的addToDisplay方法，将Window与WindowManagerService绑定。

  

Activity的Window显示过程，包括View树的绘制过程都是在Activity的ON_RESUME阶段来完成的。 — 所以在onCreate、onStart和onResume中都无法同步获取到View的宽高。

  

**5****、****Pause****阶段：执行****ActivityThread****中的****handlePauseActivity****方法。**

  

由于用户导致，如按下back键、home键、点击跳转等

调用Activity#onUserInteraction和Activity#onUserLeaveHint方法

调用onSaveInstanceState方法

  

Activity#performPause -  分发prePause、onPause和postPause事件。

  

**6****、****Stop****阶段：****handleStopActivity**

  

stop后隐藏Activity的DecorView的显示。

保证Activity是处于Pause状态

  

onSaveInstanceState调用时机：

  

1. 在Android Honeycomb之前，onSaveInstanceState在onPause调用之前被调用
2. 在Android Honeycomb之后，Android P之前，onSaveInstanceState在onStop调用之前被调用
3. 在Android P之后，onSaveInstanceState在onStop调用之后被调用

  

Activity#onStop()方法停止UI的刷新、停止运行中的动画、隐藏填充。

  

**7****、****Destroy****阶段：完成****Activity****本身的销毁逻辑、通知****System Server****处理****Activity****栈相关的逻辑。**

  

执行ActivityThread#handleDestroyActivity方法 — 调用performDestroyActivity执行本地的销毁逻辑 + 通知ATMS更新系统服务。

  

Instrumentation.callActivityOnDestroy回调用Activity的performDestroy方法，与之前的生命周期类似，performDestroy方法主要是分发preDestroy、destroy和postDestroy事件，并且会调用onDestroy生命周期回调。

  

onDestroy方法中主要是保证Activity销毁时已经关闭了所有的由此Activity管理的Dialog、Cursor和SearchDialog，可以避免一些内存泄漏。

  

  

**非生命周期关键方法分析**

  

**1****、****onSaveInstanceState —** **保存实例状态**

  

callActivityOnSaveInstanceState

1. 在Android Honeycomb（11）之前，callActivityOnSaveInstanceState在**onPause**调用**之前**被调用
2. 在Android Honeycomb（11）之后，Android P之前，callActivityOnSaveInstanceState在**onStop**调用**之前**被调用
3. 在Android P之后，callActivityOnSaveInstanceState在**onStop**调用**之后**被调用

  

  

**2****、****onRestoreInstanceState —** **恢复数据**

  

**3****、****retainNonConfigurationInstances**

  

  

  

**关键系统进程启动流程**

  

init进程 — linux/android系统用户空间的第一个进程，进程号pid为1。

  

负责创建系统中的几个关键进程。

  

Zygote进程 — Java世界的开创者。

  

init提供property service 管理安卓系统的属性。

  

  

**Code analysis:**

  

设置子进程退出的信号处理函数

  

创建一些文件夹，并挂载设备

  

设置init 的日志输出设备

  

解析init.rc配置文件

  

获得机器的硬件名：get_hardware_name() — 对应一个机器相关的配置文件，解析它

  

Init将动作Action执行的时间划分为四个阶段： early-init、init、early-boot、boot。— 划分是因为：有些动作必须在其他动作完成后才能执行。

  

开机画面：

load_565rle_image(INIT_IMAGE_FILE) 失败 输出“ANDROID”字样。

  

  

  

**Launcher** **请求** **AMS** **过程**

  

1、Launcher.startActivitySafely()

  

startActivitySafely — 

  

通过设置 FLAG_ACTIVITY_NEW_TASK flag让Activity在新的任务栈中启动。

intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK).

  

  

  

  

**Activity****启动流程**

  

Activity: 

- App 的Root Activity;
- 普通的Activity。

  

根Activity的启动过程：

- Launcher请求ATMS 过程；
- ATMS调用ApplicationThread过程；
- ActivityThread启动Activity过程。

  

ActivityThread:

- 管理应用程序进程的主线程的执行
- 执行ATMS的调度
- 执行Activity、BroadCast及相关操作。

  

ApplicationThread：

- ActivityThread的内部类，ActivityThread通过它来进行IPC调用，与SystemServer通信。

  

Instrumentation:

- 监控应用程序与系统交互
- 处理启动activity或者调用Activity、Application的生命周期

  

ActivityTaskManagerService:

- 管理Activity和它的回退栈、任务栈的系统服务

  

ActivityRecord:

system_server进程中用来描述Activity的数据类型。

存储了activity的信息，如所在的进程名称、应用的包名、所在的任务栈的taskAffinity等。

  

ActivityClientRecord:

App进程中用来描述activity的数据类型。

  

TaskRecord:

表示一个任务栈，记录Activity启动的先后顺序。

  

ActivityStack:

负责维护TaskRecord,内部保存当前Stack中所有的Task列表。

  

ActivityDisplay：

管理所有ActivityStack

  

RootActivityContainer:

作为Activity容器的根节点，负责管理所有的ActivityDisplay.

  

ActivityStackSupervisor:

Android系统中Activity的最大管家，持有RootActivityContainer来间接管理所有的Activity。

  

ClientLifecycleManager：

组合多个客户端生命周期转换和请求，作为单个事物来执行。

  

ActivityStarter是加载Activity的控制类，收集所有的逻辑来判断如何将Intent和Flags转换为Activity，并将Activity和Task以及Stack相关联。

  

**1 — Launcher****请求****ATMS** **过程**

  

Launcher#startActivitySafely ===> Activity#startActivity —> startActivity ===> Instrumentation#execStartActivity ====> 使用binder IPC 调用了 ActivityTaskManagerService，去启动Activity。 

  

  

**2 — ATMS****调用****ApplicationThread****过程**

  

判断权限信息，具备权限的调用进程才可以启动Activity。

ActivityStarter解析Intent的内容，创建对应的ActivityRecord对象，根据是否需要新建TASK来新建或者选择对应的TaskRecord添加Activity，并处理Task相关状态信息，例如前台的转移。

使前台TASK的栈顶Activity可见，这个过程会启动对应的Activity，必要情况会启动对应的进程。

通过IPC调用将启动Activity的事务发送到对应进程中，交由对应的App来处理。

  

3 —