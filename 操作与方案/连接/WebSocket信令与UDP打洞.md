#技术栈/WebSocket #技术栈/UDP #场景/P2P与NAT穿透 #状态/未完成 

### WebSocket 信令与媒体路径的边界

WebSocket 可以承载房间、SDP 和 ICE 候选等应用信令；可靠、有序是它的特性，但 WebRTC **不要求必须使用 WebSocket 或 TCP 信令**。信令需要按应用会话和端点正确投递，具体传输方式由应用选择。完整的 Offer/Answer 与候选交换见 [[概念与机制/RTC/RTC信令与建连流程]]。

媒体路径由 ICE 候选与连通性检查决定，可能直连，也可能使用 TURN 中继；不能从“用了 WebSocket 信令”推断媒体一定走 UDP 直连。原文所说低延迟偏好 UDP 是设计动机，具体路径以候选选择结果为准。[WebRTC 官方建连指南](https://webrtc.org/getting-started/peer-connections)





## ⏳ 待填补 / 待学
- [x] **WebRTC 基本建连**：见 [[概念与机制/RTC/RTC信令与建连流程]]；STUN/TURN 的具体部署与故障案例仍待补充。
- [ ] **在线游戏（FPS/MOBA）**：为什么不用WebSocket？UDP打洞如何保障高频状态同步。
- [ ] **远程桌面（如RustDesk、TeamViewer）**：打洞成功走UDP直连，失败自动无感降级走WebSocket/TURN服务器中继流量的架构设计。
- [ ] **纯聊天应用**：为何绝大多数情况只用WebSocket就够了（文字消息对延迟不敏感，直接走服务器中转更稳定可靠）。
