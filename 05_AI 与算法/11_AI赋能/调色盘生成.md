## PRD：小说调色盘APP（反抄袭调色盘生成器）

**版本**：v1.0 | **类型**：Mobile App | **面向**：网文作者、版权方

---

### 1. 背景与问题
- 手动做调色盘：两部百万字小说逐句对比，耗时数十小时
- 高级洗稿（同义词替换、语序调换）肉眼难辨
- 现有工具无语义相似度匹配，无一键导出符合平台规范的报告

### 2. 用户与场景
- **核心用户**：被抄袭的网文作者
- **场景**：发现疑似抄袭作品 → 上传两份文件 → 自动生成调色盘 → 提交投诉

### 3. 核心功能（MVP）

| 功能 | 描述 |
|------|------|
| 文件导入 | 支持 txt / docx / epub，本地读取，不联网上传 |
| 双文对比 | 用户选择“原创”与“涉嫌抄袭”两个文件 |
| 语义相似度计算 | 句子级向量匹配（同义词、语序变化鲁棒） |
| 相似度阈值过滤 | 默认70%，可调，低于阈值的不显示 |
| 调色盘表格生成 | 左右分栏，按章节/位置排序，高亮相似句 |
| 导出报告 | 导出为 PDF / 长图，符合投诉平台格式 |
| 进度提示 | 大文件处理时显示进度条，避免ANR |

### 4. 技术要点（直指核心）

| 模块 | 选型/方案 | 关键约束 |
|------|----------|----------|
| 语言/UI | Kotlin + Jetpack Compose | 现代安卓，AI生成成功率高 |
| 本地存储 | Room（存历史对比记录） | 可选 |
| 文档解析 | Apache POI（docx），epub lib（epublib或jsoup） | 注意内存 |
| 相似度算法 | 轻量级：TF-IDF + 余弦相似度（纯Java）<br>高精度：调用云端Sentence-BERT API（如HuggingFace） | MVP阶段用TF-IDF，避免本地模型体积和推理耗时 |
| 句子分块 | 按句号/感叹号/问号切分，每句最长100字 | 避免过短或过长 |
| 后台处理 | WorkManager + 协程 | 避免主线程阻塞 |
| 表格渲染 | LazyColumn + 自定义单元格 | 支持横向滚动（两栏） |
| 导出PDF | iText 或 Android PdfDocument | 注意开源协议 |
| 导出长图 | RecyclerView截图 + 拼接 | 性能注意 |

### 5. 非功能需求

- **性能**：处理10万字小说，对比时间 ≤ 30秒（本地TF-IDF），内存峰值 ≤ 256MB
- **隐私**：所有文件不上传服务器，仅本地处理
- **兼容**：minSdk 26（Android 8.0），targetSdk 33
- **崩溃率**：≤ 1%（需处理大文件OOM）

### 6. 里程碑（3周迭代）

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| P0 - 可演示原型 | 3天 | 双文本框输入、TF-IDF比对、屏幕表格展示相似句 |
| P1 - 文件处理 | +5天 | 支持txt/docx/epub读取、文件选择器、进度条 |
| P2 - 完整报告 | +5天 | 表格分页、PDF/长图导出、历史记录 |
| P3 - 优化与测试 | +8天 | 大文件性能优化、边缘测试、上架准备 |

### 7. 风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| 大文件OOM | 中 | 分块读取+流式处理，限制单文件≤50万字（MVP） |
| docx/epub解析复杂 | 中 | MVP仅支持txt，后续迭代扩展 |
| 语义匹配准确率低 | 低（TF-IDF） | 标注“基于词频相似，仅供参考”，后期可升级为云端模型 |

---

**一句话给AI/技术团队**：做一个本地优先、两文对比、输出表格+导出图片的安卓工具，相似度先用TF-IDF，UI用Compose，大文件走后台协程，先跑通再优化。

---

# 小说调色盘APP - AI落地PRD v1.0

## 目标
构建一个安卓APP，用户选择两个文本文件（原创/涉嫌抄袭），自动比对句子相似度，生成左右分栏的调色盘表格，并支持导出为图片。

## 技术栈（强制）
- 语言：Kotlin
- UI框架：Jetpack Compose（不要XML）
- 异步：Coroutines + Flow
- 本地存储：无（MVP不做历史记录）
- 文件读取：仅支持TXT（UTF-8），避免docx/epub复杂度
- 相似度算法：TF-IDF + 余弦相似度（纯Kotlin实现，不依赖外部ML库）
- 导出图片：Compose UI截图 + 保存到相册

## 项目结构（必须遵守）
```text
app/src/main/java/com/novelpalette/
├── MainActivity.kt
├── ui/
│ ├── theme/ (默认Compose主题)
│ ├── screens/
│ │ ├── FilePickerScreen.kt
│ │ └── ResultScreen.kt
├── viewmodel/
│ └── CompareViewModel.kt
├── utils/
│ ├── TextSplitter.kt
│ ├── TfidfVectorizer.kt
│ └── ScreenshotHelper.kt
└── data/
└── SentenceMatch.kt (data class)
```

## 核心代码逻辑（必须实现）

### 1. 文件选择
- 使用 `ActivityResultContracts.OpenDocument()` 选择TXT文件
- 读取后转为 `String`，显示文件名

### 2. 句子分块（TextSplitter）
- 按 `。！？；\n` 切分
- 过滤空行，每句最长100字（超出则按逗号/空格二次切分）
- 输出 `List<String>`

### 3. TF-IDF + 余弦相似度（TfidfVectorizer）
- 对原创全文所有句子构建词典（去重，词频统计）
- 计算每个句子的TF-IDF向量（维度 = 词典大小）
- 对抄袭文每个句子计算同样维度的向量
- 余弦相似度：`dot(A,B) / (norm(A)*norm(B))`
- 返回相似度 > 0.7 的匹配对 `(originalSentence, plagiarizedSentence, similarity)`

### 4. 结果展示（ResultScreen）
- 使用 `LazyColumn` 纵向滚动
- 每行是一个 `Row` 分两栏（各占一半宽度），可横向滚动（`horizontalScroll`）
- 相似度百分比显示在行上方
- 相似句子背景色标黄（`Color.Yellow`）

### 5. 导出长图（ScreenshotHelper）
- 将 `LazyColumn` 的内容包裹在 `Modifier.drawWithContent` 或使用 `GraphicsLayer` 截图
- 截取整个滚动区域的高度（需要先测量）
- 保存到 `MediaStore.Images.Media.EXTERNAL_CONTENT_URI`
- 完成后Toast提示

## 依赖版本（build.gradle.kts 核心部分）
```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.0")
    implementation("androidx.compose.ui:ui:1.5.4")
    implementation("androidx.compose.material3:material3:1.1.2")
    implementation("androidx.compose.ui:ui-tooling-preview:1.5.4")
    implementation("androidx.compose.runtime:runtime-livedata:1.5.4")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
}
```

性能约束
单文件最大10万字（约2000句子）

对比时间 < 5秒（模拟器）

禁止主线程计算，必须使用 withContext(Dispatchers.Default)

## 二、喂给AI的Prompt提示词（直接复制使用）

```text
你是一个安卓专家。请严格按照以下PRD生成完整的Android Studio项目代码，使用Kotlin + Jetpack Compose。

【需求】
小说调色盘APP：用户选择两个TXT文件（原创.txt 和 抄袭.txt），点击“比对”按钮后，系统自动分句、计算TF-IDF余弦相似度（阈值0.7），然后在第二个页面以左右两栏表格形式展示所有相似句子对（相似句子背景标黄），并提供一个“导出为图片”按钮，将整个表格截图保存到相册。

【技术约束】
- 不要XML布局，全部Compose。
- 文件选择使用 ActivityResultContracts.OpenDocument()。
- 相似度计算必须在后台线程（Dispatchers.Default），UI显示进度条。
- 句子切分规则：按 。！？；\n 切分，每句不超过100字。
- TF-IDF实现：自己写纯Kotlin代码，不要引用第三方ML库。
- 导出图片：使用 Compose 的 GraphicsLayer 截图整个滚动内容，保存到 MediaStore。
- 提供完整的 build.gradle.kts (app级别) 和 AndroidManifest.xml（包含读写权限和 file provider 如果需要）。
- 所有代码放在单个回答中，按文件结构组织，并标注文件路径。

【额外要求】
- 如果用户选择的文件过大（超过1MB），弹窗提示限制。
- 比对过程中显示环形进度条，完成后隐藏。
- 表格每行支持横向滚动（因为句子可能很长）。
- 相似度百分比显示在每对句子的上方。

请输出完整的代码工程，确保无编译错误。
