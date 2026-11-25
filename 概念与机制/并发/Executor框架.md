# Executor框架
用来实现线程池的创建和管理。

## Executor 框架的核心抽象
- 任务（Task）：Runnable 或 Callable，定义要做什么。
- 任务的执行（Execution）：Executor 负责运行任务，不关心“如何执行”（同步/异步、单线程/线程池）。
- 异步计算的结果（Result）：Future（或 CompletableFuture），用于获取异步结果、取消任务、检查完成状态。

## ThreadPoolExceutor 核心参数
- corePoolSize: 任务队列未达到队列容量时，最大可以同时运行的线程数量。
- maximumPoolSize: 任务队列中存放的任务达到队列容量时，当前可以同时运行的线程数量变为最大线程数。
- workQueue: 新任务来的时候先判断当前运行的线程数量是否达到核心线程数，若达到，则新任务被存在队列中。
- keepAliveTime: 线程中线程数量大于corePoolSize时，如果没有新的任务提交，核心线程外的线程不会立即销毁，而是等待，直到等待时间超过keepAliveTime才会被回收销毁。
- unit: keepAliveTime参数的时间单位。
- threadFactory: executor创建新线程时用到。
- handler: 拒绝策略。

## 🧾 任务
- 任务是通过 Runnable 或 Callable 接口定义的
- 提交任务的方式
  - execute
    - 不需要知道任务执行后的结果。
  - submit
    - 需要知道任务执行后的结果。

## 🫸 拒绝策略
当任务队列满、池中当前运行线程数等于最大线程数。
| 策略 | 详情 |应用场景 |
| ---- | ---- | ---- |
| AbortPolicy | 当需要显示感知任务是否被执行时。当任务被拒绝时，任务调用方会收到 RejectedExecutionException 错误。必须捕获并做出补偿。| 适合对任务丢失零容忍的场景 |
| CallerRunsPolicy | 需要所有任务都被执行，不允许丢弃任务。且容忍降低任务提交速度。当任务被拒绝时，用任务调用方的线程执行任务。形成了一种对于任务提交速度天然的反压(back pressure)机制。| - |
| DiscardPolicy | 允许任务丢失。被拒绝的任务不会留下任务痕迹。| 适合日志、监控指标上报。 |
| DiscardOldestPolicy |  只关心最新数据、旧任务可以被覆盖的场景。| 适合实时状态更新。|

## 创建线程的方式
1. 使用 ThreadPoolExecutor 构造函数直接创建。
2. 使用 Executor 工具类。
**tips: 强制不使用方法 2，容易造成资源耗尽。** 

## 🔨 tips
- 最大线程数 >= 核心线程数。
- 池共享任务队列。
- 各个线程 Worker 取任务，队列默认采用非公平策略。
- 每个工作线程被封装为 Wroker 类。
- 队列满了、工作线程数小于最大线程数。此时提交的新任务，将直接为新任务创建新的工作线程。
  - 非公平、后进先执行。
- 队列满了、工作线程数等于最大线程数。此时提交新任务，将根据拒绝策略处理。

### ❓QA
| 问题 | 回答 |
| --- | --- |
| 怎么平衡非公平策略带来的线程饥饿和核心线程数、最大线程数、keepAliveTime。 | 1. 核心线程数设足够（如 CPU 核数），让大多数任务无需激烈竞争。<br>2. 使用有界队列 + 合理最大线程数：队列满时创建新线程，打破饥饿。<br>3. keepAliveTime 设合适值（如 60s）：空闲线程回收，避免长期占用。<br>4. 可选：LinkedBlockingQueue 不设上限时易饥饿，改用 ArrayBlockingQueue 或 SynchronousQueue。<br>5. 实际策略：非公平 + 控制队列长度 + 动态扩容缩容，饥饿概率很低。|
