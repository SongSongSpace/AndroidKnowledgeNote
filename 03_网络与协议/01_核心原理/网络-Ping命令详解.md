#网络诊断 #技术栈/命令

**通** 指的是 网络层 的 IP **数据包可达性**。

#### 1、工作原理

向目标 IP 地址发送一个 ICMP 的回显请求数据包，并等待对方返回一个回显应答。

==BUT==

ping 成功并不代表 everything is ok。**只能证明基础的网络连通性**。

#### 2、应用场景

- 测量网络延迟与稳定性。回显包中会显示数据包的往返时间。
- 检测丢包率。发送的包没有全部收到应答，即存在丢包。高丢包率往往意味着网络线路质量差或者存在拥塞。
- 验证 DNS 解析。直接 ping 一个域名，即可验证。
- 安全探测。常被攻击者用于主机存活扫描，确定目标网络中有哪些设备在线。同时，也可能被滥用于发起 Ping Flood 等拒绝服务攻击。

#### 3、诞生

Mike Muuss 需要一种快速有效的 **工具** 来 **排查网络故障**，以解决他们实验室的网络异常问题。

名字来源于潜艇声纳——声纳发出脉冲，通过接收回声来探测水下目标。即对应 发送请求-等待应答 的工作模式。 Packet Internet Groper 因特网包探索器。

#### 4、使用

`ping [选项] 目标` 目标可为 IP 或域名。

示例：
- `ping 8.8.8.8`：持续 ping，Ctrl+C 停止。
- `ping -c 4 8.8.8.8`：Linux/macOS 发 4 个包。
- `ping -n 4 8.8.8.8`：Windows 发 4 个包。
- `ping -t 192.168.1.1`：Windows 持续 ping。
- `ping -i 0.5 -c 10 目标`：Linux 每 0.5 秒一次，共 10 次。
- `ping -s 1472 -c 4 目标`：Linux 指定包大小，测 MTU。
- `ping -W 2 -c 4 目标`：Linux 超时 2 秒。
- `ping -6 目标`：强制 IPv6。

不同系统 `ping` 的**默认行为不同**：
- **Linux/macOS**：默认无限发送，直到 `Ctrl+C`。所以想只发 4 个，必须加 `-c 4`。
- **Windows**：默认只发 4 个就停。所以想持续，必须加 `-t`；想指定其他数量，用 `-n`。

输出看：`time` 延迟，`ttl` 粗略判断系统，末尾丢包率和平均延迟。

#### 5、示例

发送/接收伪代码

```text
ping(目标IP, 次数=4, 超时=1秒, 间隔=1秒):
    id = 随机16位
    for seq = 1 到 次数:
        data = 当前时间戳 + 填充字节
        icmp = 构造 ICMP Echo Request:
            type = 8
            code = 0
            checksum = 0
            identifier = id
            sequence = seq
            data = data
        icmp.checksum = 计算校验和(icmp)
        ip包 = 封装IP(源=本机, 目的=目标IP, 协议=1, 载荷=icmp)
        t0 = 当前时间
        发送(ip包)

        while 未超时:
            收到包 = 接收()
            ip头, icmp回复 = 解析(收到包)
            if icmp回复.type == 0
               and icmp回复.code == 0
               and icmp回复.identifier == id
               and icmp回复.sequence == seq:
                rtt = 当前时间 - t0
                打印("来自 目标IP 的回复: icmp_seq=seq ttl=ip头.ttl time=rtt ms")
                break
        else:
            打印("请求超时")

        等待(间隔)

    打印统计: 丢包率、最小/平均/最大 RTT
```
