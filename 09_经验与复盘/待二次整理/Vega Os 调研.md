**Vega Os** **调研**

  

亚马逊 Vega OS 通过DIAL+SSDP 做本地设备发现、Message Router 做系统内消息路由、ADM 做云端推送、Matter 做跨生态互联，实现设备间发现与通信。

Vega OS = 封闭 Linux 系统 ≠ Android，普通 APK 完全无法安装 / 运行。

仅支持亚马逊应用商店内适配Vega OS的应用。

不兼容android。

亚马逊Fire TV 4K Select的系统封闭性（Vega OS）决定了安卓端功能实现需“依赖原生协议+无设备端开发”，核心可行方案均基于设备原生支持的轻量协议（SSDP/DIAL+HTTP、DLNA、Miracast），无需集成Matter SDK等大成本组件，开发成本低、可落地性强，能够满足普通用户遥控、投屏、镜像的核心需求。

  

**发现**

- 基于 UDP 广播 + SSDP/DIAL

- urn:dial-multiscreen-org:service:dial:1

  

**遥控**

Http标准化指令控制。

  

**投屏**

- Matter

- 需要额外开发电视端应用，成本大。

  

- DLNA

  

**镜像**

- Matter

- 需要额外开发电视端应用，成本大。

- Miracast

- Fire tv stick 4k select支持miracast功能
- 限制，实际不可用。

- WebRTC

  

  

matter是否支持install