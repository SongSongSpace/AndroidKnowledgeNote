# AndroidSearchView - 官方搜索示例

> Google 官方架构组件示例中的搜索实现 | 2026-04-15 | #开源项目 #搜索 #官方示例

## 🔗 项目地址
https://github.com/android/architecture-components-samples/tree/main/GithubBrowserSample

## 📝 项目简介
Google 官方的 Architecture Components 示例项目，展示 MVVM + LiveData + Room + Repository 架构。其中的搜索功能是学习「信号防抖 + 状态驱动」的官方范本。

## 🎯 核心亮点

| 亮点 | 说明 |
|------|------|
| 官方背书 | Google 团队维护，代码规范可靠 |
| 完整架构 | MVVM + Repository + LiveData |
| 搜索实现 | RxJava 的 debounce + switchMap |
| 配套能力 | 分页、缓存、网络状态处理 |

## 📁 架构层次

| 层级 | 职责 | 关键代码 |
|------|------|----------|
| View | 收集用户输入 | `EditText.addTextChangedListener()` |
| ViewModel | 暴露 LiveData，接收 query | `SearchViewModel.setQuery()` |
| Repository | 防抖 + 请求调度 | `debounce + switchMap` |
| DataSource | 实际网络请求 | `Retrofit + Call` |

## 🔑 防抖实践

Repository 层：防抖 + 切换取消
```java
Observable<Resource<List<Repo>>> searchRepos(String query) {
    return Observable.just(query)
        .debounce(500, TimeUnit.MILLISECONDS)   // 防抖 500ms
        .filter(text -> !text.isEmpty())
        .distinctUntilChanged()                 // 去重
        .switchMap(this::searchGithub)          // 自动取消旧请求
        .observeOn(AndroidSchedulers.mainThread());
}
