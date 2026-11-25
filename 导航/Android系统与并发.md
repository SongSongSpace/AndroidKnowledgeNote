# Android 系统与并发

## 按问题进入

- ANR 定位：[[故障与复盘/Android/ANR排查与治理|Android-ANR 治理与排查]]；排查主线程工作时并看 [[操作与方案/Android/Android循环与内存|Android-循环操作注意事项]]、[[操作与方案/UI/弹窗延迟实例化与动效|UI-弹窗延迟实例化躲避动效]]。
- Activity 启动链路：[[概念与机制/Android/Activity启动链路|源码-startActivity到handleLaunchActivity完整链路]]，结合 [[概念与机制/Android/Android系统启动与核心机制|源码-Android 核心机制与系统启动流程整理]] 和 [[概念与机制/Android/Android Window|源码-Window概念笔记]]。
- 并发模型：[[概念与机制/并发/Executor框架|并发-Executor框架]] → [[概念与机制/并发/线程池|并发-线程池]]；Kotlin 路线看 [[概念与机制/并发/Kotlin协程基础|并发-协程基础]] 和 [[操作与方案/并发/串行并发同步异步实践|并发-串行并发同步异步实践]]。
- 数据库迁移：[[操作与方案/Android/Android数据库版本迁移|Android-数据库版本迁移]]；其中提到 BFS，转 [[导航/算法与工程实践|算法与工程实践]]。
- 日常调试：[[操作与方案/Android/ADB调试命令|ADB-常用命令与调试实践]]。

本页按问题提供入口，技术结论仍以各正文及其验证状态为准。
