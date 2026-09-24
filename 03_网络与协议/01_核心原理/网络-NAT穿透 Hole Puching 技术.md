#网络通信 

**目标**：让两个都在 NAT/防火墙后面的设备，建立一条**直接 P2P 连接**，而不是所有数据都走公网服务器中转。

### 核心原理
1. A、B 先连接一个公网信令服务器。
2. 服务器告诉 A：B 的公网地址是 `1.2.3.4:5000`；告诉 B：A 的公网地址是 `5.6.7.8:6000`。
3. A、B **同时向对方的公网地址发包**。
4. 这些包会在各自 NAT 上创建映射/放行规则。
5. 之后双方就能直接通信，服务器只负责协调。

### 常见相关协议/技术
- STUN：发现自己的公网 IP:Port，判断 NAT 类型。RFC 8489。
- TURN：打洞失败时，用公网服务器中继流量。RFC 8656。
- ICE：综合 STUN/TURN，收集候选地址并做连通性检查。WebRTC 核心。RFC 8445。
- UDP 打洞：最常用，成功率高。
- TCP 打洞：利用 TCP 同时打开，成功率较低，受系统和 NAT 影响。
- UPnP IGD / NAT-PMP / PCP：不是严格打洞，而是向网关请求端口映射。PCP RFC 6887，NAT-PMP RFC 6886。
- Tailscale / ZeroTier / WebRTC：都包含打洞 + 中继回退机制。

### 成功条件与限制
- 锥形 NAT 成功率较高。
- 对称 NAT、CGNAT、企业防火墙下经常失败，需要 TURN 之类中继。
- 打洞本身不提供加密，通常还要叠加 TLS、DTLS、WireGuard 等。
- 需要保活包，否则 NAT 映射会过期。

### 典型应用
WebRTC 视频通话、游戏联机、P2P 下载、远程桌面、Mesh VPN、IoT 直连等。

### 伪代码

```python
sock = UDP socket
sock.bind(("0.0.0.0", 0))          # 本地端口
A_pub = stun_get_mapped(sock)       # 问 STUN 自己的公网地址
send_to_signal(A_pub)               # 告诉信令服务器
B_pub = recv_from_signal()          # 拿到对方公网地址

for i in range(100):
    sock.sendto(b"PING", B_pub)
    try:
        data, addr = sock.recvfrom(1024)
        if data == b"PING":
            sock.sendto(b"PONG", addr)
        elif data == b"PONG":
            print("打洞成功")
            break
    except BlockingIOError:
        pass
    sleep(0.02)
```

### QA

1、信令服务器怎么知道要交换？

本身不知道，是客户端主动注册到同一个会话/房间。关键是：**双方事先约定同一个房间号/会话 ID，或者由一方创建会话、另一方加入。**

