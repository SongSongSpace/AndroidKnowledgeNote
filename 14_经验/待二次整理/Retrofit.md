**是什么？**

Square 公司基于  OkHttp 封装的网络请求框架。

Retrofit 中文释义是改造。核心是把繁琐的 HTTP 请求改造成简洁的 Kotlin/Java 接口。

  

核心价值是用极简的接口注解语法，替代繁琐的 HTTP 请求底层代码。是 OkHttp 的高级封装。

  

仅适用支持 JAVA 和 Kotlin 语言。是 JVM 平台的 HTTP 框架。除了安卓，也能用于 Java 后端项目、Kotlin 后端项目。

  

**改造了什么？**

- 把 HTTP 请求改造成 面向接口编程。

- 注解代替手动拼 URL、设置请求方法。

- 自动处理 JSON 解析。
- 适配协程/挂起函数。
- 自动处理线程切换。
- 复用 OkHttp 能力。
- 简化参数传递。

  

**注解**

- 告诉框架如何构建 HTTP 请求。
- 写法依据：后端接口文档。
- 分类

- 请求方法注解：@GET / @POST / @PUT / @DELETE / @PATCH
- 参数位置注解：@Path / @Query / @Body / @Filed / @Part
- 请求头注解：@Header / @Headers
- 辅助注解：@FormUrlEncoded / @Multipart / @Streaming / @Url

- 参数值含 &、=、中文等，Retrofit会自动 URL 编码，无需手动处理。

  

**核心：按文档映射。**