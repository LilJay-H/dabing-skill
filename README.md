<div align="center">

# dabing-skill — 大冰人格蒸馏

**基于书籍语料的AI人格建模 × Claude Skill工程化实践**

[English](#english) | 中文

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![Claude Skill](https://img.shields.io/badge/skill-Claude-purple.svg)]()

</div>

---

## 项目简介

**dabing-skill** 是一个完整的 **AI人格蒸馏** 技术实践项目：从大冰（作家/主持人）的 **8本实体书、148万字** 原文语料中，通过NLP分析提取语言DNA，构建可被AI助手（Claude）直接调用的 **Skill**，实现高度还原的人格化对话。

这不是简单的提示词工程，而是一套 **可复用的人格蒸馏方法论**：

```
原始语料 → 语言分析 → 人格建模 → Skill封装 → 对话还原
```

### 项目亮点

| 特性 | 说明 |
|------|------|
| **完整语料支撑** | 8本书、1,483,413字原文提取与结构化分析 |
| **多维度语言DNA** | 句式模式（9类）、词汇风格、价值观体系、对话结构 |
| **方法论可复用** | 完整的蒸馏流程，可迁移到其他人物/IP |
| **工程化交付** | 标准Claude Skill格式，即装即用 |
| **对话还原度高** | 不是模仿语气，而是还原完整的咨询方法论 |

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/LilJay-H/dabing-skill.git
cd dabing-skill
```

### 2. 作为 Claude Skill 使用

将 `skill/` 目录复制到你的 Claude Skills 目录：

```bash
cp -r skill/ ~/.claude/skills/da-bing-perspective/
```

重启 Claude CLI 后，当用户表达成长困惑、情绪低落、人际关系问题时，Skill 自动激活。

### 3. 重新生成语料分析（可选）

```bash
cd corpus/scripts
python extract_all.py    # 从EPUB提取文本
python analyze.py        # 生成语言分析数据
```

---

## 效果示例

**场景：用户感到迷茫焦虑**

> **用户**：每天列一堆计划，最后啥也没完成，越列越焦虑
>
> **dabing-skill 回应**：
> 你那计划，是给今天的自己写的，还是给"理想中的自己"写的？
>
> 你列十条，自己看看——这日程放谁身上谁不崩溃？
>
> 今晚把计划撕了，只写三条。明天干完这三条，算你牛逼。

**关键特征还原：**
- 用问题点破认知盲区（不说教）
- 生活化类比让对方"想通"
- 给今晚就能做的最小行动
- 禁止空洞安慰词

---

## 技术架构

```
dabing-skill/
├── skill/                          # Claude Skill 核心
│   ├── SKILL.md                    #   Skill 入口（行为指令）
│   ├── da-bing-analysis.json       #   人格模型（语言DNA）
│   └── references/                 #   参考研究文档
│
├── corpus/                         # 语料库与分析工具
│   ├── books/                      #   8本书提取文本（4.1MB）
│   ├── analysis/                   #   分析结果（语录/句式/词频）
│   └── scripts/                    #   提取与分析脚本
│
└── docs/                           # 项目文档
    └── METHODOLOGY.md              #   蒸馏方法论详解
```

### 人格模型核心数据（da-bing-analysis.json）

| 维度 | 数据 |
|------|------|
| **语言特征** | 短句主体（5-15字）、口语化率极高、山东胶东方言底色 |
| **句式模式** | 9类标志性句式（排比、三段式否定、祝福收束等） |
| **对话结构** | 接住情绪 → 事实追问 → 类比拆解 → 最小行动 |
| **价值观体系** | 自由 > 稳定、江湖义气、随缘不随便 |
| **禁用词库** | "别着急"、"你已经很棒了"、"慢慢来会好的"等空洞安慰 |

---

## 蒸馏方法论

本项目的人格蒸馏流程可迁移到其他人格/IP：

### Phase 1: 语料收集
- 收集目标人物的**原始文本**（优先实体书/长文，非二次加工内容）
- 确保语料足够大（本项目：148万字）

### Phase 2: 文本处理
- EPUB/PDF/文本提取
- 按作品/篇章分段
- 编码清洗与格式统一

### Phase 3: 语言分析
- **句式模式提取**：正则匹配 + 频率统计
- **词汇风格分析**：口语/书面语比例、特色词汇、方言特征
- **价值观萃取**：高频主题词 + 上下文情感分析
- **对话结构还原**：从直播/采访记录中提取交互模式

### Phase 4: 人格建模
- 将分析结果结构化为 JSON 模型
- 包含：语言DNA + 价值观体系 + 行为准则 + 禁用规则

### Phase 5: Skill 封装
- 编写 SKILL.md（触发条件 + 行为指令）
- 场景化策略矩阵（不同问题类型的应对策略）
- 示例对话路径

> 详细方法论见 [docs/METHODOLOGY.md](docs/METHODOLOGY.md)

---

## 数据来源与版权

| 来源 | 说明 |
|------|------|
| **语料来源** | 大冰著8本实体书（2013-2022），仅用于非商业的AI人格建模研究 |
| **书籍列表** | 《他们最幸福》《乖，摸摸头》《阿弥陀佛么么哒》《好吗好的》《我不》《你坏》《小孩》《保重》 |
| **项目性质** | 技术实践项目，展示NLP分析与AI Skill工程化能力 |

本项目中的 `da-bing-analysis.json` 人格模型基于对上述书籍的文本分析生成，不包含直接复制的书籍原文段落。所有分析结论（句式模式、语言特征、价值观等）为原创研究成果。

---

## 技术栈

- **Python 3.8+**：文本提取与NLP分析
- **ebooklib**：EPUB格式解析
- **Claude Skill**：AI助手集成标准
- **JSON**：人格模型数据格式

---

## 贡献

欢迎 Issues 和 PRs！特别欢迎：

- [ ] 更多句式模式的识别与分类
- [ ] 对话效果的评估框架
- [ ] 其他人格蒸馏案例
- [ ] Skill 优化与场景扩展

---

## License

[MIT License](LICENSE)

---

<div align="center">

**如果这个项目对你有帮助，请给个 Star ⭐**

Made with ❤️ by [@LilJay-H](https://github.com/LilJay-H)

</div>

---

<a name="english"></a>

# dabing-skill — AI Personality Distillation

**Book-based NLP Personality Modeling × Claude Skill Engineering**

## Overview

**dabing-skill** is a complete **AI personality distillation** project: extracting linguistic DNA from 8 books (1.48M characters) by Da Bing (Chinese author/host), building a **Claude Skill** that enables highly authentic persona-driven conversations.

## Quick Start

```bash
git clone https://github.com/LilJay-H/dabing-skill.git
cp -r dabing-skill/skill/ ~/.claude/skills/da-bing-perspective/
```

## Key Features

- **Full corpus support**: 8 books, 1,483,413 characters analyzed
- **Multi-dimensional linguistic DNA**: 9 sentence patterns, vocabulary style, values system, dialogue structure
- **Reusable methodology**: Complete distillation pipeline for other personalities/IPs
- **Engineering-ready**: Standard Claude Skill format, plug-and-play

## Methodology

```
Raw Corpus → NLP Analysis → Personality Model → Skill Packaging → Dialogue Replication
```

## License

MIT License
