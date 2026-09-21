## 顶层结论

Android 抓屏方案的演进由**一条主线**驱动：从依赖签名权限的静默捕获，收敛为**用户显式授权 + 受控服务模型**。分水岭有二：**Android 10** 取消特权应用的静默屏幕缓冲区捕获权限，强制迁移至 MediaProjection；**Android 14** 将 MediaProjection 从“一次性授权”升级为“每会话授权”，并引入前台服务类型强制声明。Android 16 则在渲染管线层面引入 DPU 回读优化。对普通应用而言，**MediaProjection + 前台服务（类型 mediaProjection）** 是 API 21 至今唯一合规路径，差异在于权限声明粒度、生命周期管理和会话同意策略的逐步收紧。

## 一、底层权限模型演进

| 版本  | 权限模型    | 关键变化                                                                                      |
| --- | ------- | ----------------------------------------------------------------------------------------- |
| 7–9 | 签名/特权权限 | `READ_FRAME_BUFFER`、`CAPTURE_VIDEO_OUTPUT`、`CAPTURE_SECURE_VIDEO_OUTPUT` 授予签名或特权应用，支持静默捕获 |
| 10+ | 用户同意模型  | 取消特权应用视频捕获权限，未经用户同意不得捕获屏幕缓冲区；MediaProjection 成为第三方应用唯一合规路径                                |
| 14+ | 每会话同意   | 每个 MediaProjection 捕获会话均需用户单独同意，Token 不可复用                                                |
| 16  | 受控服务访问  | 屏幕捕获从运行时权限升级为受控服务访问模型，仅 system/signature/privileged 应用可发起合法请求                             |

**坑点**：Android 10 后，即使应用持有系统签名，若未迁移至 MediaProjection，`screencap` 或自定义 native 层捕获均会返回黑帧。Android 14 后，缓存 Token 复用是高频崩溃来源——`createVirtualDisplay()` 在同一 MediaProjection 实例上二次调用会直接抛出 `SecurityException。

## 二、标准抓屏步骤（API 21–35 通用流程）

**Step 1：获取 MediaProjectionManager**

```
MediaProjectionManager mpm = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
```

**Step 2：请求用户授权**

```
startActivityForResult(mpm.createScreenCaptureIntent(), REQUEST_CODE);
```

系统弹出授权对话框，Android 10 起该对话框**不可被用户隐藏**，每次启动捕获均会显示。

**Step 3：启动前台服务（Android 10+ 必须）**

在 `onActivityResult` 收到 `RESULT_OK` 后，**先启动前台服务**，再调用 `getMediaProjection()`：

```
Intent fgsIntent = new Intent(this, CaptureService.class);
fgsIntent.putExtra("resultCode", resultCode);
fgsIntent.putExtra("data", data);
startForegroundService(fgsIntent);
```

Manifest 声明：
```
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

<service
    android:name=".CaptureService"
    android:foregroundServiceType="mediaProjection" />
```

服务内：
```
startForeground(NOTIFICATION_ID, notification,
    ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
```

**Step 4：创建 VirtualDisplay**

```
MediaProjection projection = mpm.getMediaProjection(resultCode, data);
projection.registerCallback(new MediaProjection.Callback() {
    @Override
    public void onStop() {
        // Token 失效，停止捕获
    }
}, handler);
VirtualDisplay vd = projection.createVirtualDisplay(
    "capture", width, height, density,
    DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
    surface, null, null
);
```

**Step 5：从 Surface 读取帧数据**，编码为 Bitmap 或送入 MediaCodec。

## 三、各版本关键约束与踩坑清单

### Android 10（API 29）— 权限模型断崖

- **坑**：`READ_FRAME_BUFFER` 签名权限对普通应用失效，native 层 `screencap` 或 `SurfaceControl` 捕获路径全部废弃。
- **坑**：未启动前台服务直接调用 `getMediaProjection()`，在部分 OEM 设备上静默返回 null。
- **对策**：全面迁移至 MediaProjection + 前台服务，Manifest 中 `foregroundServiceType="mediaProjection"`。
### Android 12 / 12L（API 31/32）— 缩放与 Surface 对齐

- 12L 起，捕获内容渲染到 Surface 时，系统会等比例缩放至 Surface 尺寸，**不再拉伸填充**。若 Surface 宽高比与屏幕不一致，输出将出现 letterbox 黑边。
- **对策**：使用 `WindowMetrics` 获取真实屏幕尺寸，Surface 宽高比与屏幕保持一致[](https://developer.android.com/media/grow/media-projection?authuser=002&hl=bn#2)。
### Android 14（API 34）— 最密集的破坏性变更

**变更 1：每会话同意**

Token 仅可用于**单次** `createVirtualDisplay()` 调用，不可复用或缓存。

**变更 2：SecurityException 触发条件明确化**

以下操作会直接崩溃：
- 将 `getMediaProjection()` 返回的同一个 Intent 实例多次传入；
- 在同一 MediaProjection 实例上多次调用 `createVirtualDisplay()。

**变更 3：前台服务类型权限强制声明**

必须同时声明 `FOREGROUND_SERVICE` 和 `FOREGROUND_SERVICE_MEDIA_PROJECTION`，且**前台服务必须在 `getMediaProjection()` 之前启动完毕**。顺序颠倒将抛出 `SecurityException`。

**变更 4：Google Play 政策**

上架 AAB 时，`FOREGROUND_SERVICE_MEDIA_PROJECTION` 权限需在 Play Console 中提前声明类型，否则无法提交到任何 track。

### Android 15（API 35）— 应用窗口共享

Android 14 QPR2 引入、15 正式稳定：支持仅捕获**单个应用窗口**而非全屏。新增 `MediaProjection.Callback` 包括 `onCapturedContentResize()` 和 `onCapturedContentVisibilityChanged()`，用于响应捕获区域尺寸变化和可见性变化。

**坑**：应用窗口捕获时，初始尺寸需等用户选择捕获区域后才能确定，不能沿用全屏尺寸假设。

### Android 16（API 36）— DPU 回读生产化

- 引入 **DPU（Display Processing Unit）回读**生产模式，通过 `ScreenCapture` 系统 API 请求硬件加速截图。
- 启用条件：`debug.sf.productionize_readback_screenshot` 系统属性置位。
- 普通第三方应用**无法直接调用** `ScreenCapture` 系统 API（受签名保护），需通过 MediaProjection 间接受益于底层优化。
- **限制**：DPU 回读不适用于捕获屏幕内容的子集，也不适用于将 DRM 保护内容传输至非安全环境。

## 四、高频黑屏场景与根因

|场景|根因|影响范围|
|---|---|---|
|银行/支付类 App 界面|`FLAG_SECURE` 标记 Window|全版本|
|Netflix/Disney+ 等 DRM 视频播放|Widevine L1 安全层 + `FLAG_SECURE`|全版本，Android 12 后 `screencap` 同样失效|
|Android 10+ 未启动前台服务|系统拒绝 VirtualDisplay 创建|API 29+|
|Token 失效后未停止编码|`onStop` 未处理，持续产出黑帧|全版本|
|VirtualDisplay 尺寸与屏幕不匹配|12L 缩放策略导致 letterbox|API 32+|
|Android 14 重复使用 Token|`SecurityException` 直接崩溃|API 34+|

## 五、Token 生命周期管理（核心防御点）

必须注册 `MediaProjection.Callback` 并实现 `onStop()`。系统在以下场景会撤销 Token：

- 用户在 Quick Settings 中手动停止投射[](https://developer.android.google.cn/media/platform/av-capture?%3Bauthuser=1&authuser=1&hl=en#1)；
- Android 15+ 锁屏启用时自动停止；
- 源应用进程被系统回收。

**处理逻辑**：
```
@Override
public void onStop() {
    // 1. 停止 MediaCodec 编码
    // 2. 释放 VirtualDisplay
    // 3. 停止前台服务
    // 4. 清理 Surface
}
```

未注册回调的应用不会崩溃，但会**持续录制黑帧或静音流**，造成内存和 CPU 浪费[](https://developer.android.google.cn/media/platform/av-capture?%3Bauthuser=1&authuser=1&hl=en#1)。

## 六、抓屏方案选型矩阵

|方案|适用版本|权限要求|静默性|适用场景|
|---|---|---|---|---|
|`adb shell screencap`|全版本|USB 调试|依赖 ADB|开发调试、CI|
|MediaProjection + VirtualDisplay|API 21+|用户授权 + 前台服务|非静默|应用内截屏/录屏|
|`ScreenCapture` 系统 API|API 36+|system/signature|静默|系统级截图（OEM/系统应用）|
|Root + `screencap`|全版本|Root|静默|定制 ROM、企业 MDM|
|`DevicePolicyManager.setScreenCaptureDisabled`|API 21+|Device Admin|—|企业策略禁用截屏[](https://developer.android.google.cn/media/platform/av-capture?%3Bauthuser=1&authuser=1&hl=en#1)|

## 七、工程建议

1. **Token 单次性**作为不可违反的不变量：每次捕获会话前重新走 `createScreenCaptureIntent()`，禁止任何形式的 Token 缓存。
2. **前台服务启动顺序**：`startForeground()` 完成后，才调用 `getMediaProjection()` 和 `createVirtualDisplay()`。这一顺序在 Android 14 上是硬性要求。
3. **尺寸动态适配**：不要缓存屏幕尺寸。使用 `WindowMetrics.getBounds()` 每次会话重新计算，并在 Android 14+ 注册 `onCapturedContentResize()` 回调。
4. **黑帧检测**：编码前对首帧做简单像素采样，全黑或全透明则判定为 `FLAG_SECURE` 命中，向用户提示“当前页面不支持捕获”。
5. **Play Console 合规**：若使用 `FOREGROUND_SERVICE_MEDIA_PROJECTION`，提前在 Play Console 声明类型，避免 AAB 被拒。