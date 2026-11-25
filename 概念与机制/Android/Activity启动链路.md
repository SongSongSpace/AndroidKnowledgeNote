# startActivity → handleLaunchActivity 完整链路
> 跨进程启动Activity的核心流程 | 2026-04-10 | #AMS #IPC #四大组件

## 🎯 核心路径
startActivity() → Instrumentation → (IPC) → AMS → (IPC) → ApplicationThread → ActivityThread → handleLaunchActivity()

## 🔧 关键节点

| 阶段 | 所在进程 | 关键类/方法 |
|------|----------|--------------|
| 发起调用 | App进程 | `Instrumentation.execStartActivity()` |
| 第一次IPC | 跨进程 | `IActivityManager` (Binder) |
| AMS处理 | system_server | `AMS.startActivity()` → `ActivityStarter` → `ActivityStackSupervisor.realStartActivityLocked()` |
| 第二次IPC | 跨进程 | `IApplicationThread` (Binder) |
| 应用接收 | App进程 | `ApplicationThread.scheduleTransaction()` |
| 事务执行 | App进程 | `TransactionExecutor` → `LaunchActivityItem.execute()` |
| 最终回调 | App进程 | `ActivityThread.handleLaunchActivity()` → `performLaunchActivity()` |

## 📝 两次跨进程边界
1. App → system_server：`IActivityManager`
2. system_server → App：`IApplicationThread`

## ⚠️ 关键点
- `realStartActivityLocked()` 中创建 `ClientTransaction`，封装 `LaunchActivityItem`
- `handleLaunchActivity()` 内部调用 `performLaunchActivity()` 通过类加载器创建Activity实例
- 最终执行 `Activity.onCreate()`
