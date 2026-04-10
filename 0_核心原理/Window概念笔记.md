**Android Window 笔记**

**1. 本质定义**
- Window 是**抽象概念**，非实体。
- 代表“一块可接收输入、可绘制的矩形区域”的**逻辑意愿**。
- 应用端与 WMS 端关于“窗口”的契约描述。

**2. 代码实现**
- 抽象类 `Window`，唯一原生实现：`PhoneWindow`。
- `Activity` 内部硬编码创建 `PhoneWindow`，开发者无法替换。
- 抽象目的：隔离 `Activity` 与窗口策略，而非支持多态扩展。

**3. 与 Surface 的关系**
- Window 是意愿，Surface 是实体（像素缓冲区）。
- 没有 Surface，Window 无法绘制。
- 绑定通过 `ViewRootImpl` 完成：`ViewRootImpl` 持有 Surface，同时关联 Window 的参数。

**4. 与 ViewRootImpl 的关系**
- `ViewRootImpl` 在 `WindowManager.addView` 时创建。
- 它连接三端：View 树、Window（参数）、Surface（图形缓冲区）。
- 负责遍历（measure/layout/draw）与输入事件分发。

**5. 与多任务窗口的关系**
- 多任务窗口（分屏、自由窗口、画中画）是 **WMS 的布局策略**，而非新的 Window 类型。
- 每个子窗口底层仍是独立的 `Window` + `Surface`。
- 变化体现在 `WindowManager.LayoutParams` 的 flags 和 type，以及 WMS 的层级规则。

**6. 关键时机**
- `handleResumeActivity` → `wm.addView(decorView)` → 创建 `ViewRootImpl` → 请求 Surface → 异步等待 Vsync → 首帧遍历。
- `onResume` 执行时，Window 已存在，但尚未获得有效尺寸和 Surface。

**7. 核心思想**
- Window 是**逻辑边界**，不是物理资源。
- 系统的窗口管理 = 管理一堆 Window 的层级、焦点、大小、动画，而非管理像素。
- 应用与系统的窗口对话，全部通过 `WindowManager` 接口进行。

---
