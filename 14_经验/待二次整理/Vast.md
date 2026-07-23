**VAST****（****Video Ad Serving Template****）协议**

  

是一种标准协议，用于规范视频广告的投放和服务过程。

  

**<Ad>**元素包含视频播放器显示和跟踪广告素材所需的所有信息。响应可能会提供多个，但单个是最常见的。

  

多个广告是在vast3.0 才开始支持的。增加了序列属性，但。。。

  

<InLine>元素是显示广告所需的所有内容。由广告供应链中的最后一个广告服务器提供。

  

<AdSystem>返回广告的广告服务器名称

<AdTitle>广告标题

<Impression>当视频播放器在显示广告的第一帧时请求的 URI

<Creatives>一个或对个<Creative>元素

  

<Description>广告描述

<Advertiser>广告主定义的广告客户名称，用户防止与客户竞争对手展示广告

<Survey>测量 Url

<Error>错误Url 

<Pricing>价格

<Extensions>自定义节点

  

  

视频播放器必须向发送元素中提供的URI监测

  

  

**【****refrence****】**

vast 入门解析：[https://www.jianshu.com/p/ea11a65f5043](https://www.jianshu.com/p/ea11a65f5043)

vast iab :[https://iabtechlab.com/wp-content/uploads/2024/07/VAST-CTV-Addendum-2024-FINAL.pdf](https://iabtechlab.com/wp-content/uploads/2024/07/VAST-CTV-Addendum-2024-FINAL.pdf)

什么是 vast 广告？[https://hilltopads.com/blog/zh/what-is-a-vast-ad-and-how-you-can-use-it-practical/](https://hilltopads.com/blog/zh/what-is-a-vast-ad-and-how-you-can-use-it-practical/)

VAST 广告服务器响应的第三方视频插播广告 XML 摘要： [https://support.google.com/adspolicy/answer/1142000?hl=zh-Hans](https://support.google.com/adspolicy/answer/1142000?hl=zh-Hans)

投放视频广告单元 (VAST)：[https://support.google.com/authorizedbuyers/answer/6045575?hl=zh-Hans#zippy=%2C%E9%92%88%E5%AF%B9%E7%AC%AC%E4%B8%89%E6%96%B9%E5%B9%BF%E5%91%8A%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BD%BF%E7%94%A8-google-sdk%2Cvast-%E5%B0%81%E8%A3%85%E5%AE%B9%E5%99%A8%2C%E7%AC%A6%E5%90%88-ssl-%E8%A7%84%E5%AE%9A](https://support.google.com/authorizedbuyers/answer/6045575?hl=zh-Hans#zippy=%2C%E9%92%88%E5%AF%B9%E7%AC%AC%E4%B8%89%E6%96%B9%E5%B9%BF%E5%91%8A%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BD%BF%E7%94%A8-google-sdk%2Cvast-%E5%B0%81%E8%A3%85%E5%AE%B9%E5%99%A8%2C%E7%AC%A6%E5%90%88-ssl-%E8%A7%84%E5%AE%9A)