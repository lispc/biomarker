# Biomarker Knowledge Base - Agent Documentation

## 项目概述

这是一个生物标志物（Biomarker）知识库系统，包含：
- 从 CSV 读取生物标志物数据
- 使用 LLM（Moonshot API）生成说明文档
- 静态 Web 界面展示（GitHub Pages）

## 目录结构

```
.
├── marker.csv              # 生物标志物数据源（category, Biomarkers_en, Biomarkers_cn, ...）
├── query.py                # LLM 查询模块，生成单个标志物的说明文档
├── build_knowledge_base.py # 批量构建脚本，支持断点续传
├── docs/                   # GitHub Pages 部署目录
│   ├── index.html          # Web 界面
│   ├── marker.json         # CSV 转换的 JSON 数据
│   ├── .nojekyll           # 禁用 Jekyll 处理
│   └── assets/             # 生成的 Markdown 文档
│       └── ${category}/
│           └── ${index}|${en}|${cn}.md
├── assets/                 # 本地生成的文档（与 docs/assets 同步）
├── .env                    # API Key（不提交到 Git）
└── .env.example            # 环境变量示例
```

## 核心文件说明

### query.py

生成单个生物标志物的说明文档。

```python
from query import query_biomarker

# 生成单个文档
query_biomarker(
    index=1,
    name_en="Non-HDL Cholesterol",
    name_cn="Non-HDL 胆固醇",
    category="Heart & Vascular",
    output_dir="docs/assets"  # 默认
)
```

**输出文件名格式**：`{index:03d}|{name_en}|{name_cn}.md`
- 示例：`001|Non-HDL Cholesterol|Non-HDL 胆固醇.md`

**特殊字符处理**：
- `/` 和 `\` 替换为 `-`
- `|` 保留作为分隔符
- 中文保持原样

### build_knowledge_base.py

批量生成所有文档，支持断点续传。

```bash
# 生成所有未完成的文档
python build_knowledge_base.py

# 只生成前 20 个
python build_knowledge_base.py --limit 20

# 从第 100 行开始
python build_knowledge_base.py --start 100

# 指定输出目录
python build_knowledge_base.py --output-dir docs/assets
```

**断点续传逻辑**：
- 检查文件是否存在且非空
- 已存在的文件自动跳过
- 失败会打印错误但继续处理下一个

### docs/index.html

Web 界面，部署在 GitHub Pages。

**功能**：
- 左侧：分类目录树，按 CSV 顺序排列
- 搜索：支持英文名/中文名搜索
- 右侧：Markdown 渲染显示

**特殊处理**：
1. **嵌套 Markdown**：部分 LLM 输出包裹在 ` ```markdown ... ``` ` 中，会自动提取内部内容
2. **URL 编码**：中文字符编码，但保留 `|` `()` `,` 等符号不编码

## 环境配置

1. 复制环境变量示例：
```bash
cp .env.example .env
```

2. 编辑 `.env`，填入 Moonshot API Key：
```bash
MOONSHOT_API_KEY=your_api_key_here
```

3. 安装依赖：
```bash
pip install openai python-dotenv
```

## GitHub Pages 部署

1. 确保文档在 `docs/assets/` 目录下
2. 推送代码到 GitHub
3. 在仓库 Settings → Pages 中：
   - Source: Deploy from a branch
   - Branch: master / docs
4. 访问 `https://lispc.github.io/biomarker/`

## 常见修改场景

### 添加新的生物标志物

1. 在 `marker.csv` 中添加行
2. 运行构建脚本生成文档
3. 提交并 push

### 修改 Web 界面样式

编辑 `docs/index.html`：
- `<style>` 部分修改 CSS
- `<script>` 部分修改交互逻辑

### 修改 LLM 查询提示词

编辑 `query.py` 中的 `text` 变量：
```python
text = f"介绍一下 '{name_en}'（{name_cn}）这个体检指标的涵义..."
```

### 处理编码问题

如果文件名或路径出现编码错误，检查：
1. `query.py` 中的 `buildFilename` 函数
2. `build_knowledge_base.py` 中的 `build_filename` 函数（需保持一致）
3. `docs/index.html` 中的 `encodePath` 函数

## 注意事项

1. **不要提交 `.env` 文件**（已在 `.gitignore` 中）
2. **不要提交 `marker.csv`**（原始数据源，可能很大）
3. **保持 `docs/assets/` 和 `assets/` 同步**（或只使用 `docs/assets/`）
4. **LLM 输出不一致**：有的直接输出 markdown，有的包裹在代码块中，index.html 已做兼容处理

## 故障排查

### 404 错误
- 检查文件是否在 `docs/assets/` 下
- 检查 URL 编码是否正确
- 检查分类名是否匹配

### 渲染异常
- 检查是否有嵌套的 ` ```markdown ` 代码块
- 检查 marked.js 是否正确加载

### 断点续传不工作
- 检查 `build_filename` 和 `buildFilename` 逻辑是否一致
- 检查文件名中的 `|` 是否被错误替换
