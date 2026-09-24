#技术栈/WebSocket #技术栈/UDP #场景/P2P与NAT穿透 #状态/未完成 

### 一、打洞 socket  和





## ⏳ 待填补 / 待学
- [ ] **WebRTC**：详细拆解WebSocket在WebRTC中如何充当信令，ICE/STUN/TURN如何配合UDP打洞。补充STUN（获取公网IP）、TURN（中继备用）的概念。
- [ ] **在线游戏（FPS/MOBA）**：为什么不用WebSocket？UDP打洞如何保障高频状态同步。
- [ ] **远程桌面（如RustDesk、TeamViewer）**：打洞成功走UDP直连，失败自动无感降级走WebSocket/TURN服务器中继流量的架构设计。
- [ ] **纯聊天应用**：为何绝大多数情况只用WebSocket就够了（文字消息对延迟不敏感，直接走服务器中转更稳定可靠）。