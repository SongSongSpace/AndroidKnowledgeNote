**信令服务器** 交换信息：SDP Offer/Answer 和 ICE Candidates。

创建 Offer -> setLocalDescription -> 通过信令发送 -> 对端 setRemoteDescription -> 创建 Answer -> 反向交换 -> ICE 候选者交换 -> 连通性检查 -> 建立 P2P 连接。