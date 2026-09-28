#技术栈/WebRTC #RTP #网络传输

### 一、是什么？

WebRTC 是 Web Real-Time Communication，是一个支持**浏览器**、**移动应用**和**桌面应用**进行实时通信的平台，通常用于**视频通话**、**语言聊天**和**P2P文件分享**等场景。

**不是**：单一协议。
**是**：包含**媒体采集**、**编解码**、**网络传输**、**加密**等全套技术和标准的技术栈。整合在 50 多项 RFC 中。

### 二、涵盖范围

#### 媒体采集

摄像头、麦克风、屏幕捕获

#### 音视频编解码

Opus、VP8/VP9/H.264

#### 网络传输

RTP/SRTP、SCTP、UDP/TCP

#### NAT 穿透

ICE、STUN、TURN

#### ==信令协商==

SDP Offer/Answer 交换

#### 安全加密

DTLS-SRTP 默认加密所有媒体流

#### 数据通道 

RTCDataChannel 双向低延迟数据传输

### 三、基础

1、WebRTC 核心对象模型（Android Native API）[RTC-WebRTC 媒体采集API](RTC-WebRTC%20媒体采集API.md)

2、==信令与连接建立流程==

3、NAT 穿透三件套（ICE / STUN / TURN）

4、Android 权限与硬件适配

	权限：必须申请 CAMERA、RECORD_AUDIO、INTERNET、MODIFY_AUDIO_SETTINGS 等权限。
	硬件要求：在 Manifest 中声明对 摄像头 和 OpenGL ES 2.0 的硬性要求。

5、媒体轨道管理与生命周期

6、 连接状态与错误处理

7、编解码器协商与带宽适配

8、数据通道（DataChannel）的应用

9、WebRTC 协议栈底层原理

10、媒体服务器与 SFU/MCU 架构

11、跨平台互通与信令协议

12、前沿方向

- **WebAssembly + WebRTC**：在 Web 端以 Wasm 运行音视频处理逻辑，降低 CPU 占用。
- **WebTransport**：支持可靠与非可靠传输的新一代协议，被视为 WebRTC 数据通道的补充。
- **WebCodecs**：为开发者提供更细粒度的编解码控制接口。

### 四、架构总览图

```text
┌─────────────────────────────────────────────────────┐
│                    扩展层（了解）                      │
│  SFU/MCU 架构 │ 信令协议选型 │ Wasm/WebTransport     │
├─────────────────────────────────────────────────────┤
│                    进阶层（深入）                      │
│  协议栈原理 │ 音频引擎(AEC/NS/NetEQ) │ 视频引擎(拥塞控制)│
├─────────────────────────────────────────────────────┤
│                    实践层（熟练）                      │
│  轨道管理 │ 状态机与重连 │ 编解码协商 │ DataChannel    │
├─────────────────────────────────────────────────────┤
│                    基础层（必备）                      │
│  PeerConnectionFactory │ RTCPeerConnection           │
│  信令流程(SDP/ICE) │ STUN/TURN/ICE │ Android 权限     │
└─────────────────────────────────────────────────────┘
```