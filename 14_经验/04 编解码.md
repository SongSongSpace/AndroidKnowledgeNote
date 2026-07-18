Q1 airplay 官方编解码（for video and audio）分别是什么格式？
Q2 Miracast 解码？
Q3 其它内置接收器的电视设备？


### Airplay 编解码

编码
1、视频的编码格式比较单一。因为高度标准化的应用场景，即传输实时视频流。强制基准支持H.264。H.265带来更高画质和效率。
- H.265相对于H.264而言，具备更高的压缩效率。采用更灵活的编码划分（从16*16到64*64的像素。）。同画质省带宽、同码率高画质。

2、音频的编码格式需要动态协商。
- 应用场景多样。对延迟敏感的镜像使用aac_eld，对音质要求更高的纯音频流媒体播放使用alac。
- 网络状态动态适应。网络状态良好使用alac，差的时候使用aac。需要搭配协商机制。

协商过程通过**RTSP（Real Time Streaming Protocol，实时流协议）** 配合**SDP（Session Description Protocol，会话描述协议）** 完成。简单来说：
1. 接收端在SDP中“宣告”自己支持的音频编码（如`ALAC`, `AAC-ELD`）。
2. 发送端根据自身能力和需求，从列表中选择一种。
3. 双方确认后，即按此格式传输。

以上大多基于镜像。对于媒体文件播放，有不同的技术实现方式，大都不需要涉及编码。

媒体文件播放，更多是一种分享链接或文件传输。直接让接收端能访问视频文件即可，只需要地址。
1、本地视频：发送端启动一个HTTP服务器，发送端发送这个本地地址。
2、网络视频：发送端直接发送网络地址，接收端自行访问播放。

由于MP3早期是音频领域的霸主。所以支持兼容MP3是一种兼容的选择。

镜像图片。性能最好的选择是通过HTTP直接将图片文件数据post给接收端，实现更好的性能和更完整的画质。

参考开源项目，实现sender 视频文件和图片文件。参考 [**openairplay**](https://deepwiki.com/openairplay/open-airplay)[](https://deepwiki.com/openairplay/open-airplay/3.2-shell-script-client)、[**node_airtunes2**](https://www.npmjs.com/package/node-airtunes2)等开源项目。

#### 基础概念

原始数据、压缩数据、传输格式、存储格式。

视频
1、原始数据是RGB或者YUV原始像素数据。一张张的位图。
2、压缩后的格式：H.264, H.265。压缩后得到的数据包就是裸流。

音频
1、原始数据是PCM（脉冲编码调制），记录了声波的波形采样点，是未经压缩的数字信号。
2、裸流：原始数据经过压缩技术后得到的数据包。没有上下文，不知道是第几帧等详细信息。压缩后的格式：aac，alac等。
3、封装格式：将视音频裸流 + 字幕 + 元数据MetaData按照一定的格式打包进容器文件内。
- 解决音视频同步的问题。包含PTS和DTS。
- 解决随机访问的痛点。拖动进度条能通过索引快速找到对应的裸流。

#### 本地视频播放流程
1. **存储层**：`video.mp4` （**封装层**：包含H.264裸流 + AAC裸流 + 索引时间戳）
2. **解封装层**：`MediaExtractor` 把H.264和AAC的**裸流**分离开。
3. **解码层（输入）**：`MediaCodec` 接收 **H.264裸流** 和 **AAC裸流**。
4. **解码层（输出）**：`MediaCodec` 输出 **YUV原始视频帧** 和 **PCM原始音频数据**。
5. **渲染层**：Surface显示YUV，AudioTrack播放PCM。

### 编解码技术方案选型

== 受技术团队能力和产品周期等多重因素影响 ==

1、了解底层，有丰富的兼容调试经验。选择更为底层的性能更好的 MediaCodec API。
- 高性能、低能耗。
- 利用GPU进行编解码。
- 需要处理硬件兼容。
- 同时提供Java和NDK两套接口。

**OpenMAX IL**：这是Android多媒体框架（如Stagefright、NuPlayer）之下的**硬件抽象层标准**[](https://developer.baidu.com/article/detail.html?id=5630816)。它定义了上层和底层编解码器组件的统一接口，确保了MediaCodec等API能适配不同硬件

2、开发时间宽裕、周期长，功能全面。选择FFmpeg。
- 开源稳定的多媒体处理框架。
- 兼容性极佳。
- 包含多个核心库。libavcodec, libavformat等

3、追求快速开发，聚焦业务逻辑。选择基于FFmpeg或MediaCodec的封装库。
- ExoPlayer
- ijkPlayer
- MobileFFmpeg