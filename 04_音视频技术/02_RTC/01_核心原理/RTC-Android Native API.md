#技术栈/WebRTC #Native 

Android端**以什么形式**提供？
回答：以**库**的形式提供，`org.webrtc:google-webrtc`

## 一、核心对象模型

#### PeerConnectionFactory

- 全局入口，创建和管理所有 WebRTC 对象，初始化成本较高，应在应用生命周期早期创建并复用。
- 负责统一管理所有媒体源、轨道和连接对象。

#### RTCPeerConnection

连接生命周期的核心管理者，处理 *ICE 协商*、*SDP 交换*、*媒体轨道管理* 和*连接状态监控*。

#### RTCDataChannel

提供基于 SCTP 协议对等端之间的双向低延迟数据通道，适用于消息、文件传输或游戏状态同步等任意数据，不局限于音视频流。