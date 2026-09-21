# 弹窗延迟实例化躲避动效
> 避免动效期间创建/展示弹窗导致丢帧卡顿 | 2026-04-10 | #性能优化 #UI #流畅度

## 🎯 问题场景
动效执行期间（页面转场、菜单展开、列表滚动），主线程负载高。此时创建弹窗（inflate布局、measure/layout）会抢占CPU/GPU资源，导致掉帧、动画卡顿。

## 🔧 核心思路
- **延迟实例化**：不在页面初始化或动效启动时创建弹窗对象
- **延迟展示**：等待动效完全结束后再调用 `show()`

## 📝 实现方案（按推荐度排序）

| 方案 | 核心方法 | 适用场景 | 精准度 |
|------|----------|----------|--------|
| IdleHandler | `Looper.myQueue().addIdleHandler()` | 追求极致流畅 | ⭐⭐⭐⭐⭐ |
| TransitionListener | 监听转场动画结束回调 | Activity/Fragment转场 | ⭐⭐⭐⭐ |
| onWindowFocusChanged | 监听窗口获得焦点 | 简单页面 | ⭐⭐⭐ |
| postDelayed | `view.postDelayed(time)` | 固定短时动效 | ⭐⭐ |

## 📝 核心代码片段（IdleHandler版）

```kotlin
class IdleDialogShower(private val dialogProvider: () -> Dialog) {
    fun showWhenIdle() {
        Looper.myQueue().addIdleHandler {
            dialogProvider().show()
            false  // 单次执行
        }
    }
}

// 使用
IdleDialogShower { AlertDialog.Builder(context).create() }.showWhenIdle()
```

## ⚠️ 注意事项
IdleHandler延迟不可控，弹窗可能稍晚出现
postDelayed需估算动效时长，低端机可能仍会卡顿
务必在页面销毁时取消延迟任务，避免内存泄漏

## 核心原则
让出动效执行权 → 动效完成 → 空闲/回调时机 → 实例化并展示
