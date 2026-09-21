# 一、SDP 是什么，已经它为什么存在

**背景**：WebRTC 旨在实现两个浏览器之间的实时音视频通信。
**问题**：在两个浏览器建立连接之前，对彼此一无所知。

在连接之前，**需要掌握的**：对方支持什么音视频解码器、用什么 IP 地址和端口来接收数据、是否支持视频、加密方式是什么。

SDP（Session Description Protocol）就是用来说明**本端可承担的功能范围与能力边界，以及本端拟采用的通信机制/协议**的==**格式约定**==。
	**不是**：传输协议。
	**不做**：传输任何媒体数据。
	**是**：用一种双方都能够解析的文本格式，将能力与功能以及拟通信机制通过**信令通道**交换出去。

协商：WebRTC的协商遵循 **Offer/Answer 模型**——发起方创建 Offer，接收方回应 Answer，双方通过 SDP 的交换达成一致。

# 二、SDP 的基本结构：会话级 + 媒体级

**是**：一系列文本行，每行格式为 `<type>=<value>`，`<type>` 是单个大小写敏感的字符。

**会话级**：描述整个会话的全局信息，从 `v=` 开始，到第一个 `m=` 之前结束。

**媒体级**：每个 `m=` 行开启一个媒体段，描述一路具体的媒体流（音频、视频或数据）。会话级的某些设置会被媒体级的同名设置覆盖。

行有固定顺序要求。

# 三、逐行拆解

### 会话级

`v=0`
`o=- 4962303333179871722 1 IN IP4 0.0.0.0`
`s=-`
`t=0 0`

v 协议版本，目前永远是 0。
o 会话发起者信息，格式为 `o=<username> <sess-id> <sess-version> <nettype> <addrtype> <address>` 。
s 会话名称。无实际意义，固定为 - 。
t 会话活跃时间。`t=0 0` 表示会话不设时间限制。

`a=group:BUNDLE a1 v1`
`a=ice-options:trickle`
`a=msid-semantic:WMS`

`a=group:BUNDLE a1 v1` 指示音频和视频的 m= 行使用同一个传输通道。
`a=ice-options:trickle` 表示支持 Trickle ICE，即 ICE 候选可以边收集边发送，不必等全部收集完再发。
`a=msid-semantic:WMS` 定义媒体流标识语义，用于将多个 track 关联到同一个 MediaStream。

### 媒体级

`m=audio 10100 UDP/TLS/RTP/SAVPF 96 0 8 97 98`，格式：==m=<媒体类型> <端口> <传输协议> <负载类型列表...>``==

媒体类型：audio、video 或 application。数据通道使用 application。
端口：接收该媒体的端口号。
传输协议：UDP/TLS/RTP/SAVPF 是 WebRTC 的标准值——UDP 承载，TLS 加密，RTP 用于媒体，SAVPF 表示带反馈的安全音频视频配置文件。
负载类型列表：一组数字，每个数字对应一个具体的编解码格式。

### 连接信息

c= 行。如 `c=IN IP4 203.0.113.100` 。指示媒体传输的目标网络地址。
但：在WebRTC 中，真正的可达地址由 ICE 候选决定。c= 只是一个占位符。

媒体关键属性

`a=mid:` 媒体标识符。用于在 BUNDLE 分组中引用这个 `m=`字段： `a=mid:a1`。
`a=sendrecv`：方向属性。表示这个媒体既可以发送也可以接收。`sendonly` `recvonly` `inactive`。
`a=rtpmap:`：将 `m=`行中的数字负载类型映射到具体的编解码器。
	`a=rtpmap:96 opus/48000/2`
	`a=rtpmap:0 PCMU/8000`
	`a=rtpmap:8 PCMA/8000`
`a=fmtp:`：编解码器的附加参数。
`a=extmap:`：RTP 头部扩展映射。

### ICE 相关属性

`a=ice-ufrag` 和 `a=ice-pwd`：ICE 身份验证凭证，双方用它们来验证连接检查请求的合法性。
`a=candidate:` 候选地址，格式包含候选类型（`host` 表示本机地址，`srflx` 表示通过 STUN 发现的公网映射地址）、优先级、IP、端口和传输协议。
`a=end-of-candidates`：标识候选收集已完成。在 Trickle ICE 场景下，候选会在 Offer/Answer 发送后通过信令单独发送，这个标记表示不再有新的候选了。

### DTLS 安全相关属性

`a=fingerprint`：DTLS 证书的哈希指纹。双方在 DTLS 握手时交换证书，并比对证书的哈希值是否与 SDP 中的 fingerprint 一致，以此来防止中间人攻击。
`a=setup`：DTLS 连接的角色协商。`actpass` 表示“我既可以主动发起也可以被动接受”，由 Answer 方决定最终角色（`active` 或 `passive`）。

# 四、Offer/Answer 完整流程与示例

### 流程概览

1. Alice 调用 `createOffer()`，浏览器生成包含上述所有信息的 SDP Offer。
2. Alice 通过信令服务器将 Offer 发送给 Bob。
3. Bob 收到 Offer 后，调用 `setRemoteDescription()`，再调用 `createAnswer()`，生成自己的 SDP Answer。
4. Bob 将 Answer 通过信令服务器发回 Alice，Alice 调用 `setRemoteDescription()` 设置远端描述。
5. ICE 连通性检查完成后，媒体开始传输。

### 简化的 Offer

```
v=0
o=- 4962303333179871722 1 IN IP4 0.0.0.0
s=-
t=0 0
a=ice-options:trickle
a=group:BUNDLE a1 v1

m=audio 10100 UDP/TLS/RTP/SAVPF 96 0 8 97 98
c=IN IP4 203.0.113.100
a=mid:a1
a=sendrecv
a=rtpmap:96 opus/48000/2
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:97 telephone-event/8000
a=rtpmap:98 telephone-event/48000
a=fmtp:97 0-15
a=fmtp:98 0-15
a=ice-ufrag:074c6550
a=ice-pwd:a28a397a4c3f31747d1ee3474af08a068
a=fingerprint:sha-256 29:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73...
a=setup:actpass
a=candidate:0 1 UDP 2113667327 192.168.1.4 10100 typ host
a=end-of-candidates

m=video 10100 UDP/TLS/RTP/SAVPF 120 121
c=IN IP4 203.0.113.100
a=mid:v1
a=sendrecv
a=rtpmap:120 VP8/90000
a=rtpmap:121 rtx/90000
a=fmtp:121 apt=120
a=ice-ufrag:074c6550
a=ice-pwd:a28a397a4c3f31747d1ee3474af08a068
a=fingerprint:sha-256 29:E2:1C:3B...
a=setup:actpass
a=candidate:0 1 UDP 2113667327 192.168.1.4 10100 typ host
a=end-of-candidates
```

1、`a=group:BUNDLE a1 v1`：代表音视频复用同一个传输通道。从两条媒体流的端口都是 10100，且 ICE 凭证和 fingerprint 相同，这都是 BUNDLE 生效的表现。2、actpass 表示我方愿意接受任一角色。

### Answer

```
m=audio 10100 UDP/TLS/RTP/SAVPF 96
a=mid:a1
a=sendrecv
a=rtpmap:96 opus/48000/2
a=ice-ufrag:c300d85b
a=ice-pwd:de4e99bd291c325921d5d47efbabd9a2
a=fingerprint:sha-256 6B:8B:F0:65:5F:78:E2:51...
a=setup:active
a=candidate:0 1 UDP 2113667327 192.168.1.5 10100 typ host
a=end-of-candidates
```

这条回答表明：1、对方选择了 96 映射的格式作为音频编解码器。2、双方互发。3、对方主动发起DTLS 握手。由于我方 actpass 表示愿意接受任一角色，所以对方作出最终决定。

# 五、重要概念

### BUNDLE：让音视频公用一个通道

每个 m= 段如果各自使用独立端口和 ICE 连接，WebRTC 的建连开销会翻倍。BUNDLE 扩展允许将多个 m= 段绑定到一个传输通道上。

实现方式很简单：在会话级加 `a=group:BUNDLE a1 v1`，然后各个 m= 段使用**相同的端口和相同的 ICE 凭证**。这样 ICE 只需要对一组地址做连通性检查，DTLS 也只需要握手一次。

### Trickle ICE：不必等候选收集完

传统流程要求 ICE 候选全部收集完毕后才发送 Offer/Answer，但在网络环境复杂时，收集所有候选可能需要数秒。Trickle ICE 允许在 Offer/Answer 中只包含部分候选（甚至不含候选），后续通过信令通道逐步发送 `a=candidate` 行，`a=end-of-candidates` 标记结束。这能显著缩短建连延迟[](https://datatracker.ietf.org/doc/html/draft-uberti-rtcweb-rfc8829bis-05#10)。

# 六、核心价值

‼️ 理解**协商逻辑**：
- Offer 说“我能做这些”，Answer 从 Offer 的子集中选“我们就用这些”。
- Answer 不能凭空创造 Offer 中不存在的编解码器或属性。
- 方向（sendrecv/sendonly/recvonly）决定了媒体的流向。
- ICE 候选和 DTLS fingerprint 是 WebRTC 特有的扩展，标准 SDP（RFC 4566）本身不包含这些，它们是 WebRTC 生态在 SDP 上的叠加。