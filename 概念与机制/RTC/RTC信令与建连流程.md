# RTC 信令与建连流程

核对日期：2026-11-25。范围：两个端点使用 `RTCPeerConnection` 建立一次连接的基本路径；不规定具体应用的信令协议、重连策略或媒体服务器实现。

## 先区分三件事

- **信令**：应用把 SDP offer/answer 和 ICE 候选传给对端。WebRTC 不规定应用必须用 WebSocket；HTTP、WebSocket 等都可承载应用信令。[WebRTC 官方建连指南](https://webrtc.org/getting-started/peer-connections)
- **SDP 协商**：双方描述要收发的媒体、编解码能力及传输参数。Offer/Answer 的具体内容见 [[概念与机制/RTC/WebRTC SDP]]。
- **ICE 连通性检查**：双方收集候选地址并测试候选对。可经 STUN 得到候选，也可能借 TURN 中继；连接成功不等于一定是设备间直连。网络前置知识见 [[概念与机制/网络/NAT]]、[[概念与机制/网络/NAT穿透]]。[RFC 8445](https://www.rfc-editor.org/rfc/rfc8445)

## 一次典型的 Offer/Answer

| 顺序 | 发起端 A | 接收端 B |
|---|---|---|
| 准备 | 创建连接，配置所需 ICE 服务器和媒体轨道/收发方向 | 创建连接，准备媒体轨道/收发方向 |
| Offer | `createOffer()` → `setLocalDescription(offer)` → 经应用信令发送 offer | 收到 offer 后 `setRemoteDescription(offer)` |
| Answer | 经应用信令收到 answer 后 `setRemoteDescription(answer)` | `createAnswer()` → `setLocalDescription(answer)` → 经应用信令发送 answer |
| 候选 | 收集到本地 ICE 候选时经信令发送；收到对端候选后 `addIceCandidate()` | 同样发送本地候选并添加对端候选 |
| 连通性 | ICE 测试候选对并选出可用路径；观察连接状态 | 同时参与检查，可能走直连或 TURN 中继 |

这个表描述**逻辑先后**，不是“等 Answer 完成才开始收集或交换候选”的串行时间线。使用 Trickle ICE 时，候选可以随收集逐条发送，与 Offer/Answer 交换交叠；也可以等收集完成后把候选包含在 SDP 中。收到候选时应确认对应的远端描述已经就绪；过早到达的候选由应用按所用 API 的要求暂存与处理。[RFC 8838](https://www.rfc-editor.org/rfc/rfc8838)、[W3C WebRTC API](https://www.w3.org/TR/webrtc/)

## 到什么状态才算通了

完成 SDP 交换只表示两端知道如何协商，**不证明网络路径已经可用**。继续观察 `iceGatheringState`、`iceConnectionState` 和 `connectionState`；`connected` 说明连接已建立，但还要分别核对预期媒体轨道、收发方向、实际音视频和数据通道是否工作。连接失败时按阶段定位，不能只看“信令消息已送达”。[WebRTC 官方建连指南](https://webrtc.org/getting-started/peer-connections)

| 断点 | 优先核对 |
|---|---|
| Offer/Answer 无法应用 | 双方是否按顺序设置本地/远端描述；SDP 协商错误和信令是否送错会话 |
| 候选未交换或无法连通 | `icecandidate` 是否发送、对端是否调用 `addIceCandidate()`、候选与会话是否匹配、STUN/TURN 配置及网络可达性 |
| 状态已 connected 但没有媒体 | 轨道是否加入、方向是否符合预期、接收端是否消费轨道；再查编解码与播放链路 |

实际项目应为信令消息关联会话和端点，并处理重复、迟到、断线与重新协商；这些属于应用设计，不是 WebRTC 自动提供的业务协议。[[操作与方案/连接/WebSocket信令与UDP打洞]] 记录了一个候选架构，但 WebSocket 是选型，不是 WebRTC 的必需组件。
