> 涵盖 Java/Android 并发编程、Android 系统源码、网络基础以及底层架构设计。

## 01_并发编程
- [[并发-Executor框架]] : Java 线程池底层原理与任务调度机制
- [[并发-协程基础]] : Kotlin 协程的挂起、恢复与调度器
- [[并发-线程池]] : 线程池核心参数与调优实践
- [[并发-串行并发同步异步实践]] : 实际场景中并发模型的选择与踩坑

## 02_Android 系统源码
- [[源码-APT注解处理原理]] : 编译期注解处理器（APT）工作流程与源码剖析
- [[源码-startActivity到handleLaunchActivity完整链路]] : Activity 启动的完整 Framework 链路
- [[源码-Window概念笔记]] : Window、WindowManager 与 WindowManagerService 机制

## 03_网络基础
- [[网络-三次握手]] : TCP 连接建立机制（*关联：也可在 `00_网络与协议_MOC` 中找到*）

## 04_代码实践与性能
- [[Android-循环操作注意事项]] : 循环中的内存分配与 I/O 避坑
- [[Android-ANR 治理与排查]] : 主线程阻塞、ANR 日志分析与治理方案

## 05_架构与设计
- [[Android-数据库版本迁移]] : 数据库迁移框架设计、APT 与代理模式应用

## ⏳ 待填补 / 待学
- [ ] JVM 内存模型与 GC 机制
- [ ] Binder 跨进程通信原理
- [ ] 系统启动流程（Zygote/SystemServer）