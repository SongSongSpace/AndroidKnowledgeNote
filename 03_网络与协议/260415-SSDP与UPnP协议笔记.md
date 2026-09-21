# SSDP 与 UPnP 协议笔记

> 简单服务发现协议 + 通用即插即用 | 2026-04-15 | #网络协议 #SSDP #UPnP #设备发现

## 🎯 核心概念

| 协议 | 全称 | 作用 |
|------|------|------|
| **UPnP** | Universal Plug and Play | 设备无缝连接和互操作的整套架构 |
| **SSDP** | Simple Service Discovery Protocol | UPnP 的核心组件，负责设备发现 |

**一句话**：SSDP 是 UPnP 用来「找设备」的协议。

## 📝 UPnP 架构层次

| 层次 | 协议/技术 | 作用 |
|------|----------|------|
| 寻址 | DHCP / AutoIP | 设备获取 IP 地址 |
| **发现** | **SSDP** | 设备加入网络，控制点寻找设备 |
| 描述 | XML | 获取设备能力详情 |
| 控制 | SOAP | 调用设备动作 |
| 事件 | GENA | 监听设备状态变化 |
| 展示 | HTML | 提供 Web 控制界面 |

## 📝 SSDP 核心机制

### 消息类型

| 消息 | 方向 | 说明 |
|------|------|------|
| `M-SEARCH` | 控制点 → 组播 | 主动搜索网络中设备 |
| `NOTIFY` | 设备 → 组播 | 设备上线/下线通知 |
| `HTTP 200 OK` | 设备 → 控制点 | 单播响应 M-SEARCH |

### 组播地址

| 参数 | 值 |
|------|-----|
| 组播地址 | `239.255.255.250` |
| 端口 | `1900` |
| 协议 | UDP |

### 消息示例

```http
M-SEARCH * HTTP/1.1
HOST: 239.255.255.250:1900
MAN: "ssdp:discover"
MX: 3
ST: upnp:rootdevice
```
### 📝 SSDP 工作流程
```text
1. 设备上线
   └── 发送 NOTIFY（组播）→ 通知所有控制点

2. 控制点搜索
   └── 发送 M-SEARCH（组播）→ 询问谁在线

3. 设备响应
   └── 发送 HTTP 200 OK（单播）→ 告诉控制点自己的信息

4. 设备下线
   └── 发送 NOTIFY with ssdp:byebye
```

### 🔑 核心要点
|要点|	说明|
|--- | --- |
|无中心服务器	|完全去中心化的设备发现|
|组播通信	|一发多收，无需预先知道对方地址|
|即插即用	|设备上线自动通知，无需手动配置|
|基于 |HTTP/UDP	SSDP 使用 UDP 组播，响应和描述使用 HTTP|

### 📝 典型应用场景
|场景|	说明|
|---| ---|
|智能电视投屏	|手机发现电视设备|
|打印机发现	|电脑自动发现网络打印机|
|路由器管理	|通过 UPnP 自动端口映射|
|智能家居	|发现灯泡、插座、音箱|

### 📝 与 Android 的关系
|组件	|说明|
|---| ---|
|android.net.wifi	|WiFi 管理，组播锁|
|MulticastLock	|接收组播包需要申请|
|DatagramSocket	|UDP 收发 SSDP 消息|
|HttpURLConnection	|获取设备描述 XML|

### Android 组播锁示例
```java
WifiManager wifi = (WifiManager) getSystemService(WIFI_SERVICE);
MulticastLock lock = wifi.createMulticastLock("ssdp");
lock.acquire();  // 获取组播锁
// 收发 SSDP 消息...
lock.release();  // 释放
```

### 🔑 关联笔记
[[Lighthouse - 状态驱动的网络设备搜索](7_开源项目/260415-Lighthouse.md)]

[[AndroidSearchView - 官方搜索示例](7_开源项目/260415-AndroidSearchView.md)]
