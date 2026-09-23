#技术栈/WebRTC #Native 

Android端**以什么形式**提供？
回答：以**库**的形式提供，`org.webrtc:google-webrtc`

## 一、核心对象模型

#### PeerConnectionFactory

全局入口，创建和管理所有 WebRTC 对象，初始化成本较高，应在应用生命周期早期创建并复用。

#### RTCPeerConnection

连接生命周期的核心管理者，处理 ICE 协商、SDP 交换、媒体轨道管理和连接状态监控。

#### RTCDataChannel

提供对等端之间的双向低延迟数据通道，适用于消息、文件传输或游戏状态同步。

## 二、信令与建立连接流程

**信令服务器** 交换信息：SDP Offer/Answer 和 ICE Candidates。

创建 Offer -> setLocalDescription -> 通过信令发送 -> 对端 setRemoteDescription -> 创建 Answer -> 反向交换 -> ICE 候选者交换 -> 连通性检查 -> 建立 P2P 连接。