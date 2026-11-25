# Lighthouse - 状态驱动的网络设备搜索

> 局域网设备发现 + 状态驱动架构 | 2026-04-15 | #开源项目 #状态驱动 #协程

## 🔗 项目地址
https://github.com/ivanempire/lighthouse

## 📝 项目简介
Lighthouse 是一个 Android 局域网设备发现库，通过 SSDP 协议搜索网络中的设备（如智能电视、音箱、打印机等）。核心亮点是用 **Kotlin 协程 + Flow** 实现状态驱动的设备管理。

## 🎯 核心亮点

| 亮点 | 说明 |
|------|------|
| 状态驱动 | 追踪网络中所有设备状态，变化时自动发射给消费者 |
| 现代技术栈 | Kotlin + Coroutines + Flow |
| 搜索模型 | 封装单播/组播 M-SEARCH 消息 |
| 响应式 | 设备上下线实时通知 |

## 🔑 可学习点

| 学习点 | 具体内容 |
|------|----------|
| Flow 状态管理 | 使用 StateFlow 管理设备列表状态 |
| 协程并发 | 多设备搜索的协程并发控制 |
| 防抖应用 | 设备状态变化的防抖处理 |
| 协议封装 | SSDP 协议的 Kotlin 封装实践 |

## 📝 核心代码思路（伪代码）

```kotlin
class Lighthouse {
    private val _devices = MutableStateFlow<List<Device>>(emptyList())
    val devices: StateFlow<List<Device>> = _devices.asStateFlow()
    
    fun startDiscovery() {
        viewModelScope.launch {
            ssdpSearch()  // 发送 M-SEARCH
                .flatMapMerge { response ->  // 并发处理响应
                    parseDevice(response)
                }
                .collect { device ->
                    updateDeviceState(device)  // 状态更新
                }
        }
    }
}
```
