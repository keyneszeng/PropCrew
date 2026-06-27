# 🏡 房地产销售 Agent 智能体 — 产品需求文档 (PRD)

> **文档版本**: v1.0 | **日期**: 2026-06-27 | **状态**: 待评审
> **编写**: AI Architect | **交付对象**: 研发团队

---
## 目录
1. [项目概述](#1-项目概述)
2. [产品定位与价值](#2-产品定位与价值)
3. [用户角色与场景](#3-用户角色与场景)
4. [功能需求](#4-功能需求)
5. [核心流程](#5-核心流程)
6. [Agent 详细定义](#6-agent-详细定义)
7. [Skill 详细定义](#7-skill-详细定义)
8. [数据模型](#8-数据模型)
9. [技术栈要求](#9-技术栈要求)
10. [非功能性需求](#10-非功能性需求)
11. [合规要求](#11-合规要求)
12. [交付物清单](#12-交付物清单)
13. [分期实施计划](#13-分期实施计划)
14. [验收标准](#14-验收标准)

---
## 1. 项目概述

### 1.1 项目背景
房地产经纪人每天需要产出大量内容（短视频脚本、小红书笔记、客户话术等）来获客和维护客户关系。
但经纪人普遍缺乏内容创作能力和时间，导致：
- 内容质量参差不齐，影响获客效果
- 合规风险高（广告法违规、虚假承诺等）
- 优质案例无法复制和复用
- 跨平台内容运营效率低下

本产品旨在构建一个 **房地产销售 Agent 智能体系统**，通过 AI 辅助经纪人完成从内容策划、生成、质检到发布的全流程工作。

### 1.2 项目目标

| 目标 | 衡量指标 |
|------|---------|
| 提升内容产出效率 | 1 条内容需求 → 5 分钟内产出草稿 |
| 降低合规风险 | 合规违规率 < 1%（规则引擎拦截） |
| 提高内容质量 | 经纪人采纳率 > 80% |
| 多平台覆盖 | 支持 抖音/小红书/朋友圈/企微 4 个平台 |


---
## 2. 产品定位与价值

### 2.1 产品定位
> **一句话描述**: 房地产经纪人的专属 AI 内容中台，一个人就是一个内容团队。

### 2.2 核心价值

| 价值 | 说明 |
|------|------|
| 🎯 **内容生产自动化** | 从房源信息到多平台内容（脚本/笔记/话术）一键生成 |
| 🛡️ **合规风险拦截** | 内置房产广告法规则引擎，内容发布前自动审查 |
| 📊 **数据驱动选题** | 基于发布记录和成交数据分析，自动推荐下周选题 |
| 🔄 **经验可复制** | 成交案例 → 内容素材模板，优秀经验沉淀复用 |
| 💬 **线索转化提效** | 客户触达话术智能生成，提升邀约和转化率 |

### 2.3 竞品差异

| 对比项 | 通用 AI 助手 (ChatGPT/DeepSeek) | 本产品 |
|--------|-------------------------------|--------|
| 房地产专业知识 | 通用知识，不深入 | 内置房产政策/广告法/板块数据 |
| 合规审查 | 不提供 | 规则引擎+LLM 双层质检 |
| 多 Agent 协作 | 单轮对话 | 内容总监编排 6 个专业 Agent |
| 知识库 | 无 | 房源/板块/政策/模板/案例 5 大库 |
| 素材复用 | 无 | 成交案例自动转化为素材模板 |

---
## 3. 用户角色与场景

### 3.1 用户角色

| 角色 | 说明 | 核心需求 |
|------|------|---------|
| 🏢 **房产经纪人** | 一线销售，负责房源带看和客户转化 | 快速产出内容，合规安全 |
| 👑 **店长/经理** | 管理团队内容产出和质量 | 审核内容，分析团队发布效果 |
| 🏛️ **合规专员** | 公司层面的内容风控 | 设定合规规则，审查高风险内容 |

### 3.2 核心使用场景

| # | 场景 | 触发方式 | 期望产出 | 使用频率 |
|---|------|---------|---------|---------|
| S1 | 经纪人想发一条小红书的探房笔记 | 输入: "帮我把 XX 小区写成小红书" | 完整笔记（标题+正文+标签） | 每天 3-5 次 |
| S2 | 想拍摄一个探房短视频 | 输入: "XX 房源拍个探房视频" | 分镜脚本+口播文案 | 每周 2-3 次 |
| S3 | 客户在评论区问价格/学区 | 输入: 评论截图或文字 | 回复话术 | 每天 5-10 次 |
| S4 | 发了 5 条笔记但没有咨询量 | 输入: "看看我这周数据" | 复盘报告 + 下周选题建议 | 每周 1 次 |
| S5 | 新出了限购政策，想发科普内容 | 输入: "解读一下新政" | 科普文案/脚本 | 每月 1-2 次 |
| S6 | 成交了一套房，想分享案例 | 输入: "XX 小区成交案例" | 成交故事素材 | 每周 1-2 次 |

---
## 4. 功能需求

### 4.1 功能全景图

```
┌─────────────────────────────────────────────────────────────┐
│                      经纪人 Web UI                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎯 内容创作模块            💬 线索转化模块                  │
│  ┌─────────────────┐       ┌─────────────────┐              │
│  │ · 小红书笔记生成  │       │ · 评论回复生成   │              │
│  │ · 短视频脚本生成  │       │ · 私信跟进话术   │              │
│  │ · 政策科普内容    │       │ · 电话邀约话术   │              │
│  │ · 成交案例素材化  │       │ · 异议处理话术   │              │
│  └─────────────────┘       └─────────────────┘              │
│                                                             │
│  📊 数据分析模块            ⚙️ 系统管理模块                   │
│  ┌─────────────────┐       ┌─────────────────┐              │
│  │ · 发布效果复盘    │       │ · 房源资料管理   │              │
│  │ · 下周选题推荐    │       │ · 知识库管理     │              │
│  │ · 板块趋势分析    │       │ · 合规规则配置   │              │
│  └─────────────────┘       └─────────────────┘              │
│                                                             │
│  🛡️ 合规中心                                                │
│  ┌──────────────────────────────────────────┐               │
│  │ · 内容发布前自动审查 · 合规规则自定义      │               │
│  │ · 违规历史记录   · 合规评分看板          │               │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 功能清单（按优先级分组）

#### P0 - MVP 核心功能（必须）

| ID | 功能 | 描述 | 关联 Agent |
|----|------|------|-----------|
| F-001 | **用户输入处理** | 接收经纪人的自然语言指令（文字/语音），识别意图 | 内容总监 |
| F-002 | **小红书笔记生成** | 输入房源/小区信息，自动生成完整小红书笔记（标题+正文+标签+emoji） | 小红书文案顾问 |
| F-003 | **短视频脚本生成** | 输入房源卖点，生成探房/口播类分镜脚本（含口播文案+镜头建议） | 短视频编导 |
| F-004 | **房源卖点提炼** | 从房源资料中自动提取核心卖点、风险点、目标客群 | 房源卖点分析师 |
| F-005 | **内容合规审查** | 发布前自动检查违禁词、虚假承诺、政策误导（规则引擎+LLM） | 合规质检员 |
| F-006 | **小区板块信息查询** | 查询小区周边学校、交通、商业、竞品信息 | 小区板块研究员 |
| F-007 | **评论/私信回复生成** | 针对客户评论和私信生成个性化回复 | 线索转化顾问 |

#### P1 - 增强功能（第二阶段）

| ID | 功能 | 描述 | 关联 Agent |
|----|------|------|-----------|
| F-008 | **政策科普内容生成** | 输入政策原文，生成通俗易懂的科普文章/脚本 | 政策科普转化 Skill |
| F-009 | **成交案例素材化** | 成交案例 → 可复用的内容模板（故事/话术/脚本） | 成交案例素材化 Skill |
| F-010 | **发布效果复盘** | 分析历史发布数据（阅读/互动/转化），生成复盘报告 | 复盘分析 Skill |
| F-011 | **下周选题推荐** | 基于数据分析和热门趋势，推荐下周内容选题 | 选题策划 Skill |
| F-012 | **话术模板管理** | 管理不同场景的客户触达话术模板 | 线索转化顾问 |
| F-013 | **素材模板库** | 管理已验证的爆款标题/封面/段子模板 | 小红书文案顾问 |

#### P2 - 优化功能（第三阶段）

| ID | 功能 | 描述 |
|----|------|------|
| F-014 | **AI 检测规避** | 内容自动改写以降低被平台识别为 AI 生成的概率 |
| F-015 | **多平台一键发布** | 对接抖音/小红书 API，内容一键发布 |
| F-016 | **企业微信消息推送** | 话术直接推送到企微，一键复制发送 |
| F-017 | **CRM 数据对接** | 对接现有 CRM 系统，自动同步房源和客户数据 |
| F-018 | **批量内容生成** | 一次输入多套房源，批量生成不同平台内容 |
| F-019 | **用户反馈闭环** | 经纪人评分 + 采纳率统计，自动优化 Agent Prompt |
| F-020 | **多模型路由** | 简单任务用 DeepSeek，复杂任务用 GPT-4o，成本优化 |

---
## 5. 核心流程

### 5.1 小红书笔记生成流程（主流程）

```
┌────────────────────────────────────────────────────────────────────┐
│ 输入: "帮我写一篇 XX 小区的探房小红书"                               │
└────────────────────────┬───────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│ 🎯 内容总监 - 意图识别 & 任务拆解                                     │
│                                                                     │
│ 意图=内容创作 | 平台=小红书 | 类型=探房笔记                           │
│ 拆解: [并行] 卖点分析 + 板块研究 → [串行] 笔记撰写 → 合规质检        │
└────────────────────────┬───────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              │
┌─────────────────────┐ ┌─────────────┐ │
│ 🔍 卖点分析师        │ │ 📊 板块研究员 │ │
│ 读取房源资料库        │ │ 查询小区库   │ │
│ 输出卖点JSON          │ │ + 地图 API  │ │
│ +前置合规标记         │ │ 输出板块报告 │ │
└──────────┬──────────┘ └──────┬──────┘ │
           │                  │         │
           └──────────────────┘         │
                      │                 │
                      ▼                 │
┌─────────────────────────────────────┐ │
│ 🎯 内容总监 - 归集上下文               │ │
│ 传给: 小红书文案顾问                  │ │
└──────────────────┬──────────────────┘ │
                   │                    │
                   ▼                    │
┌─────────────────────────────────────┐ │
│ ✍️ 小红书文案顾问                      │ │
│ 选择笔记类型 → 查询素材模板库            │ │
│ 生成标题+正文+emoji+标签               │ │
│ AI检测规避改写 → 输出笔记草稿           │ │
└──────────────────┬──────────────────┘ │
                   │                    │
                   ▼                    │
┌─────────────────────────────────────┐ │
│ ⚖️ 合规质检员 (双层)                   │◄┘
│ Layer1 规则引擎: 违禁词匹配           │
│ Layer2 LLM语义: 隐含风险识别         │
│ 输出: 合规报告 + 修改建议             │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ 🎯 内容总监 - 终审                     │
│ 汇总笔记草稿 + 合规报告 → 返回给用户    │
│ 用户可: 采纳/修改/重新生成             │
│ 用户反馈 → 记录用于Prompt优化          │
└─────────────────────────────────────┘
```

### 5.2 合规审查流程（关键流程）

```
用户提交内容
      │
      ▼
┌─────────────────────────────────────────────┐
│ Layer 1: 规则引擎 (强制)                      │
│                                             │
│ 1. 违禁词匹配 (正则扫描词表)                   │
│    例: "升值" "第一" "学区房" "保证收益"       │
│                                             │
│ 2. 广告法敏感词扫描                           │
│    例: "最" "首个" "国家级" "绝版"            │
│                                             │
│ 3. 学区承诺检测                              │
│    例: "签约XX名校" "入读XX小学"              │
│                                             │
│ 4. 价格表述合规                              │
│    例: "首付xx万起" 需注明具体房源             │
│                                             │
│ 结果: 有匹配? ──是──► 标记 + 替换建议 ──► 输出     │
│        │ 否                                  │
│        ▼                                    │
│                                            │
│ Layer 2: LLM 语义判断 (辅助)                 │
│                                             │
│ 1. 上下文风险判断 (整段内容语义)              │
│ 2. 隐含承诺识别 ("这套房子以后肯定涨")        │
│ 3. 误导性表述检测 (数据引用是否准确)           │
│                                             │
│ 结果: 有嫌疑? ──是──► 标记嫌疑 + 说明 ──► 输出    │
│        │ 否                                  │
│        ▼                                    │
│  输出: 通过 ✅                                │
└─────────────────────────────────────────────┘
```

### 5.3 政策科普内容生成流程（新增）

```
输入: "解读一下最新的公积金贷款新政"
      │
      ▼
┌─────────────────────────────────────────┐
│ 🎯 内容总监                               │
│ 意图=政策科普 → 路由到政策科普转化 Skill   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ 政策科普转化 Skill                        │
│                                          │
│ 1. 从政策法规库检索最新公积金政策原文       │
│ 2. 从外部政策数据源确认政策时效性           │
│ 3. 政策解读:                               │
│    ├── 原文 → 通俗解释                     │
│    ├── 购房者影响: 首付/利率/额度变化       │
│    ├── 业主影响: 交易/过户/税费变化         │
│    └── 行动建议: 哪些人该做什么             │
│ 4. 方案:                                   │
│    ├── [方案A] 小红书科普笔记              │
│    ├── [方案B] 短视频口播脚本              │
│    └── [方案C] 朋友圈转发文案              │
│                                          │
│ 输出: 科普内容初稿 + 方案建议               │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ ⚖️ 合规质检 (双层)                         │
│ Layer1: 政策引用必须注明出处和生效日期      │
│ Layer1: 不得曲解政策原意                   │
│ Layer2: LLM 检查解读是否准确              │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ 🎯 内容总监 - 终审 + 返回用户             │
└─────────────────────────────────────────┘
```

---
## 6. Agent 详细定义

### 6.1 Agent 总览

| Agent | 角色 | 输入 | 输出 | 依赖 Skill | 调用模型建议 |
|-------|------|------|------|-----------|------------|
| 🎯 内容总监 | 任务总控/主编 | 用户指令 | 任务 DAG + 终审结果 | 选题策划 | DeepSeek V3 |
| 🔍 卖点分析师 | 房源信息提取 | 房源资料 | 结构化卖点 JSON（含合规标记） | 卖点提炼 | DeepSeek V3 |
| 📊 板块研究员 | 板块趋势研究 | 小区名称 | 板块研究报告 | 无独立 Skill | GPT-4o/Claude |
| 🎬 短视频编导 | 脚本创作 | 卖点/板块报告 | 分镜脚本（口播+镜头+时长） | 脚本生成、成交案例素材化 | DeepSeek V3 |
| ✍️ 小红书文案 | 笔记创作 | 卖点/板块报告 | 完整笔记（含AI规避改写） | 笔记撰写 | DeepSeek V3 |
| 💬 线索转化 | 话术生成 | 客户问题/画像 | 话术建议（含多备选） | 话术生成 | DeepSeek V3 |
| ⚖️ 合规质检 | 内容风控 | 任意待发布内容 | 合规报告（通过/警告/拦截） | 合规检查（规则引擎+LLM） | 规则引擎:Python; LLM: DeepSeek |

### 6.2 Agent 通信协议

```json
// 请求格式
{
  "task_id": "uuid-string",
  "agent_type": "property_analyst | district_researcher | video_director | xiaohongshu_writer | lead_converter | compliance_officer",
  "input": {
    "data": {},
    "context": {
      "user_id": "str",
      "previous_agents": ["coordinator"],
      "references": ["property_uuid_123"],
      "shared_bus": {}  // Agent 中间结果共享总线
    },
    "instructions": "提取卖点，标注学区风险"
  },
  "config": {
    "model": "deepseek-v3 | gpt-4o",
    "temperature": 0.3,
    "max_tokens": 2000
  }
}

// 响应格式
{
  "task_id": "uuid-string",
  "status": "success | error | partial",
  "output": {},
  "confidence": 0.95,
  "risk_flags": ["学区承诺风险"],
  "compliance": {
    "status": "pass | warning | blocked",
    "rule_matches": [],
    "ai_concerns": []
  },
  "metadata": {
    "model": "deepseek-v3",
    "tokens_used": 1500,
    "latency_ms": 3200
  }
}
```

### 6.3 Agent Prompt 要点

#### 🎯 内容总监
```
角色: 你是一个资深的房地产内容主编（总编）。
任务: 
  1. 分析用户指令，识别意图类型（内容创作/政策科普/线索转化/数据分析）
  2. 拆解任务为子任务，判断串行/并行关系
  3. 选择合适的 Agent 执行子任务
  4. 跟踪执行状态，处理异常
  5. 汇总结果，做最终合规把关
注意: 
  - 如果用户提到政策/新政/限购/贷款等 => 路由到政策科普转化 Skill
  - 如果用户提到"看看数据/复盘/效果" => 路由到复盘分析
  - 最终输出必须经过合规质检
```

#### ✍️ 小红书文案顾问
```
角色: 你是一个精通小红书爆款笔记的房地产文案专家。
任务: 根据房源卖点和板块信息，生成一篇高互动率的小红书笔记。

写作风格要求:
  - 标题: 使用数字+悬念+emoji，如 "😱 XX小区业主都惊了！3个秘密只有老业主知道"
  - 正文: 真人语气，口语化，避免"您好""请问"等官方用语
  - 结构: 痛点描述 → 实景体验 → 干货输出 → 引导互动
  - emoji: 每段1-2个，自然嵌入
  - 结尾: 引导评论/私信，如 "姐妹们还想看哪个小区？评论区告诉我"

笔记类型模板:
  1. 收藏型: 干货攻略，结构清晰，带小标题
  2. 攻略型: 步骤分解，如"买房3步走"
  3. 同城种草型: 本地人视角，突出地理位置和周边配套
  4. 避坑型: 真实踩坑经历，引发共鸣
  5. 买家故事型: 成交客户故事，真实感强

合规红线 (必须遵守):
  - 不能写 "升值""暴涨""学区房""保证收益"
  - 不能承诺 "签约XX学校""入读XX小学"
  - 不能使用 "最""第一""国家级" 等广告法违禁词
  - 价格描述需注明"具体以实际房源为准"

AI检测规避（必须执行）:
  - 避免 AI 常见句式: "首先...其次...最后" "综上所述" "值得注意的是"
  - 加入真人语气词: "说实话""我跟你讲""真的"
  - 段落长度不均，避免整齐划一的排版
  - 加入个人感受和细节描述
```

#### ⚖️ 合规质检员
```
角色: 你是房产内容的合规审查专家，熟悉《广告法》《房地产广告发布规定》。

规则引擎 (Layer 1 - 必须执行):
  - 逐条扫描违禁词列表
  - 检测价格承诺、学区承诺、升值承诺
  - 识别广告法禁用词汇

语义判断 (Layer 2 - 辅助):
  - 上下文是否存在隐含的承诺/误导
  - 整体语气是否有诱导性
  - 数据引用是否合理

输出格式:
  - 通过: 无任何风险
  - 警告: 有风险但可修改
  - 拦截: 必须修改后才能发布
  
每条风险必须提供:
  - 问题描述（具体哪句话/哪个词）
  - 违规类型（违禁词/价格法/学区法/广告法）
  - 严重程度
  - 修改建议
```

---
## 7. Skill 详细定义

### 7.1 Skill 清单

| Skill ID | Skill 名称 | 输入 | 输出 | 依赖数据 | 关联 Agent |
|----------|-----------|------|------|---------|-----------|
| SK-01 | 卖点提炼 | 房源资料（户型/面积/价格/装修/楼层/图片描述） | JSON { location, transportation, education, layout, price_value, target_audience, risk_points, compliance_flags } | 房源资料库 | 🔍 卖点分析师 |
| SK-02 | 脚本生成 | 卖点JSON + 板块报告 + 素材模板 | 分镜脚本 { scenes: [{type, duration, content, camera, bgm}] } | 素材模板库 | 🎬 短视频编导 |
| SK-03 | 笔记撰写 | 卖点JSON + 板块报告 + 素材模板 + 笔记类型 | 笔记 { title, content, tags, emoji_strategy } | 素材模板库 | ✍️ 小红书文案 |
| SK-04 | 选题策划 | 发布记录 + 热门趋势 + 客户问题 | 选题列表 { topics: [{title, reason, expected_effect}] } | 发布记录库 | 🎯 内容总监 |
| SK-05 | 话术生成 | 客户问题/画像 + 场景类型 + 话术模板 | 话术列表 { options: [{text, reason, suitability}] } | 话术模板库 | 💬 线索转化 |
| SK-06 | 合规检查 | 任意待发布文本 | 合规报告 { status, rule_matches[], ai_concerns[], suggestions[] } | 违禁词表 + 政策法规库 | ⚖️ 合规质检 |
| SK-07 | 复盘分析 | 发布记录 + 互动数据 | 复盘报告 { summary, metrics, insights, recommendations } | 发布记录库 | 🔍 卖点/📊 板块 |
| SK-08 | 📌 政策科普转化 | 政策原文 | 科普内容 { summary, impact_analysis, action_guide, output_plans[] } | 政策法规库 | 🎯 内容总监 |
| SK-09 | 📌 成交案例素材化 | 成交案例数据 | 素材模板 { reusable_formats: [title_template, story_template, script_template] } | 成交案例库 | 🎬 编导/✍️ 文案 |

### 7.2 Skill 输出格式标准

#### SK-01: 卖点提炼 输出格式
```json
{
  "property_id": "uuid",
  "basic_info": {
    "title": "XX小区3室2厅",
    "area": 120,
    "price": 5800000,
    "price_per_sqm": 48333,
    "rooms": "3室2厅",
    "floor": "15/30",
    "decoration": "精装修",
    "orientation": "南北通透"
  },
  "selling_points": [
    {"point": "核心卖点", "detail": "南北通透，全明户型", "priority": 1},
    {"point": "交通优势", "detail": "距地铁XX站300米", "priority": 2},
    {"point": "价格优势", "detail": "同户型低于均价5%", "priority": 3}
  ],
  "target_audience": "改善型家庭/学区需求/通勤族",
  "risk_points": [
    {"category": "噪音", "detail": "临街，白天车流量较大"},
    {"category": "房龄", "detail": "建成10年，外立面需维护"}
  ],
  "compliance_flags": [
    {"type": "学区警告", "detail": "虽然小区对口XX小学，但政策可能变化，不能承诺入读"}
  ]
}
```

#### SK-06: 合规检查 输出格式
```json
{
  "status": "warning",
  "rule_matches": [
    {
      "word": "学区房",
      "position": "正文第2段",
      "category": "学区",
      "severity": "高",
      "suggestion": "改为'周边有教育配套'"
    },
    {
      "word": "升值",
      "position": "标题",
      "category": "价格",
      "severity": "高",
      "suggestion": "改为'价值保持'"
    }
  ],
  "ai_concerns": [
    {
      "type": "隐含承诺",
      "detail": "文中提到'这套房子您不用担心'，有暗示承诺的嫌疑",
      "suggestion": "改为'这套房子在同类型中表现不错'"
    }
  ],
  "suggestions": [
    "1. 将标题中'升值'替换为'高性价比'",
    "2. 第2段'学区房'替换为'周边配套齐全'",
    "3. 第5段具体房源价格建议注明'此房源为例，其他房源以实际为准'"
  ]
}
```

---
## 8. 数据模型

### 8.1 核心实体

```sql
-- 房源表
CREATE TABLE property (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    address TEXT,
    district VARCHAR(50),
    price DECIMAL(12,2),
    area DECIMAL(8,2),
    rooms VARCHAR(20),
    floor VARCHAR(20),
    total_floors INT,
    decoration VARCHAR(50),
    property_type VARCHAR(20) CHECK (property_type IN ('new', 'resale', 'rent')),
    tags JSONB DEFAULT '[]',
    images JSONB DEFAULT '[]',
    selling_points JSONB,
    compliance_flags JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 小区表
CREATE TABLE community (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    address TEXT,
    district VARCHAR(50),
    avg_price DECIMAL(12,2),
    build_year INT,
    schools JSONB DEFAULT '[]',
    transportation JSONB DEFAULT '[]',
    commercial JSONB DEFAULT '[]',
    competition JSONB DEFAULT '[]',
    price_trend JSONB,
    poi_data JSONB,  -- 高德/百度地图POI数据
    last_updated TIMESTAMP DEFAULT NOW()
);

-- 政策法规表
CREATE TABLE policy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    source VARCHAR(100),  -- 住建部/央行/地方房管局
    publish_date DATE,
    effective_date DATE,
    content TEXT,
    summary TEXT,
    version INT DEFAULT 1,
    change_log JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    vector_embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 发布记录表
CREATE TABLE post (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES property(id),
    agent_id VARCHAR(100),
    platform VARCHAR(20) CHECK (platform IN ('douyin', 'xiaohongshu', 'wechat', 'weibo')),
    content_type VARCHAR(20) CHECK (content_type IN ('script', 'note', 'talk_script', 'popular_science')),
    content JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'pending_review', 'approved', 'rejected', 'published')),
    compliance_report JSONB,
    publish_time TIMESTAMP,
    engagement_metrics JSONB DEFAULT '{}',
    user_feedback INT CHECK (user_feedback BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 素材模板表
CREATE TABLE template (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_type VARCHAR(50) CHECK (template_type IN ('title', 'cover', 'talk_script', 'story', 'opening')),
    platform VARCHAR(20),
    content_type VARCHAR(20),
    template_text TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    success_score DECIMAL(3,2) DEFAULT 0,
    tags JSONB DEFAULT '[]',
    vector_embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 违禁词表
CREATE TABLE banned_word (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    word VARCHAR(200) NOT NULL,
    severity VARCHAR(10) CHECK (severity IN ('high', 'medium', 'low')),
    category VARCHAR(50) CHECK (category IN ('school_district', 'price', 'finance', 'promise', 'ad_law')),
    regex_pattern VARCHAR(500),
    replacement_suggestion TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 客户线索表
CREATE TABLE lead (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100),
    source VARCHAR(50),
    customer_info JSONB,
    intention_level INT CHECK (intention_level BETWEEN 1 AND 5),
    property_match JSONB DEFAULT '[]',
    conversation_history JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'contacted', 'invited', 'visited', 'closed', 'lost')),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 8.2 向量知识库集合

| 集合名 | 嵌入字段 | 用途 | 相似度搜索场景 |
|--------|---------|------|--------------|
| property_vectors | 房源描述 + 卖点 | 语义搜索相似房源 | "找一个和XX小区相似的房源" |
| community_vectors | 小区描述 + 板块数据 | 板块研究语义匹配 | "XX板块有什么特点" |
| policy_vectors | 政策原文 + 通俗解读 | 政策引用 + 合规检查 | "限购政策有哪些要求" |
| template_vectors | 素材模板文本 | 内容生成模板匹配 | "找一个爆款标题模板" |
| case_vectors | 成交案例 + 转化链路 | 成交案例素材化 | "帮我写这个成交案例的故事" |

### 8.3 违禁词表（MVP 版）

```json
[
  {"word": "升值", "category": "price", "severity": "high", "replacement": "保持价值"},
  {"word": "暴涨", "category": "price", "severity": "high", "replacement": "价格有上涨趋势"},
  {"word": "学区房", "category": "school_district", "severity": "high", "replacement": "周边教育配套齐全"},
  {"word": "名校旁", "category": "school_district", "severity": "high", "replacement": "附近有学校"},
  {"word": "签约入读", "category": "school_district", "severity": "high", "replacement": "请咨询教育部门(以当年政策为准)"},
  {"word": "保证收益", "category": "finance", "severity": "high", "replacement": "仅供参考"},
  {"word": "投资必涨", "category": "finance", "severity": "high", "replacement": "自住投资两相宜"},
  {"word": "第一", "category": "ad_law", "severity": "high", "replacement": "领先"},
  {"word": "最", "category": "ad_law", "severity": "high", "replacement": "非常"},  
  {"word": "首个", "category": "ad_law", "severity": "high", "replacement": "早期"},
  {"word": "国家级", "category": "ad_law", "severity": "high", "replacement": "经相关部门批准"},
  {"word": "绝版", "category": "ad_law", "severity": "medium", "replacement": "稀缺"},
  {"word": "遥遥领先", "category": "ad_law", "severity": "medium", "replacement": "备受关注"},
  {"word": "首付xx万起", "category": "price", "severity": "medium", "replacement": "首付x万起（此房源为例，具体以实际为准）"},
  {"word": "零风险", "category": "finance", "severity": "high", "replacement": "低风险（需具体说明）"}
]
```

---
## 9. 技术栈要求

### 9.1 开发技术栈

| 层级 | 技术选型 | 版本要求 | 说明 |
|------|---------|---------|------|
| **后端语言** | Python | >= 3.12 | Agent 编排和 LLM 调用 |
| **Agent 框架** | LangChain + LangGraph | latest | 支持 DAG 编排，状态图管理 |
| **API 框架** | FastAPI | >= 0.110 | REST + WebSocket 接口 |
| **LLM 主模型** | DeepSeek V3 API | - | 性价比最优，日常任务主力 |
| **LLM 复杂模型** | GPT-4o / Claude 3.5 Sonnet | - | 板块研究、复杂内容生成 |
| **规则引擎** | Python re + 自定义规则类 | - | 合规检查 Layer 1，100% 可解释 |
| **向量数据库** | ChromaDB (dev) / PGVector (prod) | latest | 知识库语义搜索 |
| **关系数据库** | SQLite (dev) / PostgreSQL 16 (prod) | - | 结构化数据存储 |
| **任务队列** | Redis + Celery | - | 生产环境异步任务编排 |
| **前端** | React 18 + TypeScript / Vue3 + Tailwind | - | 经纪人 Web 端 |
| **容器化** | Docker + Docker Compose | - | 开发/生产部署 |

### 9.2 开发环境要求

```
├── Python 3.12+
├── Node.js 18+ (前端)
├── Docker Desktop (可选)
├── Git
├── LLM API Key (DeepSeek / OpenAI)
└── 8GB+ RAM, 20GB+ 磁盘空间
```

### 9.3 Python 依赖（核心）

```txt
# 核心
langchain>=0.2.0
langgraph>=0.1.0
fastapi>=0.110.0
uvicorn[standard]

# LLM
openai>=1.0.0
deepseek-sdk (如提供)

# 向量/数据库
chromadb>=0.5.0
sqlalchemy>=2.0
asyncpg>=0.29  # PostgreSQL driver

# 工具
pydantic>=2.0
redis>=5.0  # 生产环境
celery>=5.3  # 生产环境

# Web UI (MVP)
streamlit>=1.30

# 前端 (正式版)
react>=18
tailwindcss>=3.4
axios
```

---
## 10. 非功能性需求

### 10.1 性能指标

| 指标 | 目标值 | 衡量方式 |
|------|-------|---------|
| 单次内容生成响应时间 | < 3 分钟（含合规检查） | 端到端计时 |
| LLM 调用延迟 | < 5 秒/次 | API 响应时间 |
| 并发支持 | 支持 50 经纪人同时使用 | 压力测试 |
| 合规检查时间 | < 3 秒（规则引擎）+ < 10 秒（LLM） | 计时 |
| 知识库检索延迟 | < 500ms | 向量搜索计时 |
| 系统可用性 | 99.5% (月) | 排除了 LLM API 异常 |

### 10.2 安全性要求

| 要求 | 说明 |
|------|------|
| API 鉴权 | 所有 API 接口需 JWT 令牌认证 |
| 数据加密 | 客户联系方式、房源信息等敏感数据加密存储 |
| 审计日志 | 所有 Agent 执行记录可追溯 |
| LLM 内容安全 | LLM 输出经过合规双层检查后才返回用户 |
| 数据隔离 | 不同经纪公司的数据严格隔离 |

### 10.3 成本控制

| 项目 | 目标 | 说明 |
|------|------|------|
| 单次调用成本 | < ¥0.05 | DeepSeek V3 为主模型 |
| 月成本 (单个经纪人) | < ¥30 | 日均 20 次任务 × 30 天 |
| 总月成本 (50 人团队) | < ¥3000 | 含基础设施和 API 费用 |
| 成本优化策略 | 多模型路由 | 简单任务 DeepSeek，复杂任务 GPT-4o |

### 10.4 可扩展性

| 维度 | 要求 |
|------|------|
| Agent 扩展 | 新增 Agent 只需实现统一的通信协议，不影响已有 Agent |
| Skill 扩展 | Skill 为独立模块，可热插拔 |
| 平台扩展 | 新增内容平台只需增加对应的输出模板 |
| 数据源扩展 | 新增数据源只需实现数据接入适配器 |
| 模型扩展 | 新增 LLM 模型只需增加 Model Adapter |

---
## 11. 合规要求

### 11.1 房地产广告法律依据

| 法规 | 关键要求 |
|------|---------|
| 《广告法》第九条 | 不得使用"最""第一"等绝对化用语 |
| 《房地产广告发布规定》 | 房源信息需真实，不得承诺升值、学区 |
| 《广告法》第二十六条 | 房地产广告面积需表明是建筑面积或套内面积 |
| 《广告法》第二十八条 | 虚假广告的定义和处罚 |
| 地方性房地产广告规定 | 各地具体要求（需定期更新） |

### 11.2 合规检查清单（研发实现时依此编码）

```
检查项清单（规则引擎 Layer 1）
├── ✅ 违禁词匹配
│   ├── 扫描违禁词表（见 8.3）
│   ├── 支持正则模式匹配（如 "首付\d+万起"）
│   └── 支持上下文扩展（如 "签约"+"学校" = 学区承诺）
│
├── ✅ 价格表述合规
│   ├── "最低价" "抄底价" "跳楼价" → 拦截
│   ├── "首付xx万起" → 需注明"此房源为例"
│   └── "升值" "暴涨" "翻倍" → 拦截
│
├── ✅ 学区承诺检测
│   ├── "学区房" "名校旁" → 替换
│   ├── "签约XX学校" "入读XX学校" → 拦截
│   └── "XX学校划片" → 需注明"以当年教育部门政策为准"
│
├── ✅ 金融类用语
│   ├── "保证收益" "零风险" → 拦截
│   ├── "投资必涨" "稳赚" → 拦截
│   └── 贷款利率描述需注明"具体以银行审批为准"
│
├── ✅ 广告法违禁词
│   ├── "最"系列: 最好/最大/最低/最优 → 替换
│   ├── "一"系列: 第一/首个/唯一/首家 → 替换
│   ├── "级"系列: 国家级/顶级/极品 → 替换
│   └── "虚假承诺": 保证/承诺/确保 → 拦截
│
└── ✅ 房源信息真实性
    ├── 面积的"建筑面积"或"套内面积"标注
    ├── 价格注明"此房源为例，实际以房源为准"
    └── 图片不得过度美化（AI 生成图片需标注）
```

### 11.3 合规报告输出标准

所有内容在返回用户前，必须附带合规报告。

**合规报告的优先级规则：**
1. 如果有任何 "high" 级别的违禁词命中 → status = "blocked"，必须修改
2. 如果有 "medium" 级别违禁词命中 → status = "warning"，建议修改
3. 如果 LLM 发现语义风险 → status = "warning"，标注嫌疑点
4. 如果没有任何风险 → status = "pass"

**展示给用户的方式：**
- 🟢 通过: 整条内容绿色边框，显示✅ 合规通过
- 🟡 警告: 黄色边框，高亮风险词，显示修改建议按钮
- 🔴 拦截: 红色边框，内容不可发布，必须修改后才显示"确认"按钮

---
## 12. 交付物清单

### 12.1 研发交付物

| # | 交付物 | 说明 | 交付阶段 |
|---|--------|------|---------|
| D-01 | **项目源码仓库** | GitHub/GitLab 仓库，包含完整代码 | Phase 1 |
| D-02 | **API 文档** | FastAPI 自动生成 Swagger UI | Phase 1 |
| D-03 | **数据库 DDL 脚本** | 建表 SQL 脚本 | Phase 1 |
| D-04 | **违禁词表 JSON** | 可配置的违禁词列表文件 | Phase 1 |
| D-05 | **Agent Prompt 配置** | 各 Agent 的 Prompt 模板（YAML/JSON） | Phase 1 |
| D-06 | **Docker Compose 配置** | 一键部署配置 | Phase 2 |
| D-07 | **测试用例文档** | 核心流程的测试用例 | Phase 1 |
| D-08 | **部署手册** | 开发/生产环境部署指南 | Phase 2 |
| D-09 | **用户操作手册** | 经纪人使用指南 | Phase 3 |

### 12.2 项目目录结构

```
real-estate-agent/
├── README.md                     # 项目说明
├── docker-compose.yml            # Docker 部署
├── requirements.txt              # Python 依赖
├── pyproject.toml                # 项目配置
│
├── agent/                        # Agent 核心代码
│   ├── __init__.py
│   ├── coordinator.py            # 🎯 内容总监 Agent
│   ├── property_analyst.py       # 🔍 卖点分析师 Agent
│   ├── district_researcher.py    # 📊 板块研究员 Agent
│   ├── video_director.py         # 🎬 短视频编导 Agent
│   ├── xiaohongshu_writer.py     # ✍️ 小红书文案 Agent
│   ├── lead_converter.py         # 💬 线索转化 Agent
│   └── compliance_officer.py     # ⚖️ 合规质检 Agent
│
├── skills/                       # Skill 实现
│   ├── __init__.py
│   ├── selling_point_extractor.py    # SK-01
│   ├── script_generator.py           # SK-02
│   ├── note_writer.py                # SK-03
│   ├── topic_planner.py              # SK-04
│   ├── talk_generator.py             # SK-05
│   ├── compliance_checker.py         # SK-06 (规则引擎)
│   ├── review_analyzer.py            # SK-07
│   ├── policy_converter.py           # SK-08
│   └── case_to_template.py           # SK-09
│
├── core/                         # 框架核心
│   ├── __init__.py
│   ├── agent_base.py             # Agent 基类
│   ├── skill_base.py             # Skill 基类
│   ├── task_manager.py           # 任务管理与编排
│   ├── context_bus.py            # Shared Context Bus
│   └── model_router.py           # 多模型路由
│
├── knowledge/                    # 知识库
│   ├── __init__.py
│   ├── vector_store.py           # 向量存储
│   ├── property_db.py            # 房源资料库
│   ├── community_db.py           # 小区/板块库
│   ├── policy_db.py              # 政策法规库
│   ├── template_db.py            # 素材模板库
│   └── banned_words.py           # 违禁词表
│
├── api/                          # API 接口
│   ├── __init__.py
│   ├── main.py                   # FastAPI 入口
│   ├── routes/
│   │   ├── content.py            # 内容生成接口
│   │   ├── lead.py               # 线索转化接口
│   │   ├── analysis.py           # 数据分析接口
│   │   └── admin.py              # 管理配置接口
│   └── models/
│       └── schemas.py            # Pydantic 模型
│
├── web/                          # 前端（MVP 用 Streamlit）
│   └── app.py                    # (Phase 1 用 Streamlit)
│
├── config/                       # 配置文件
│   ├── prompts/                  # Agent Prompt 模板
│   │   ├── coordinator.yaml
│   │   ├── property_analyst.yaml
│   │   ├── district_researcher.yaml
│   │   ├── video_director.yaml
│   │   ├── xiaohongshu_writer.yaml
│   │   ├── lead_converter.yaml
│   │   └── compliance_officer.yaml
│   ├── banned_words.json         # 违禁词列表
│   └── settings.py               # 环境配置
│
├── tests/                        # 测试
│   ├── test_coordinator.py
│   ├── test_selling_point.py
│   ├── test_compliance.py
│   └── test_workflow.py
│
└── docs/                         # 文档
    ├── PRD.md                    # 本文件
    ├── ARCHITECTURE.md           # 架构设计
    └── FEASIBILITY_REVIEW.md     # 可行性审查
```

---
## 13. 分期实施计划

### 13.1 总体路线图

```
Phase 1 (1-2周)         Phase 2 (+1周)          Phase 3 (+2周)          Phase 4 (持续)
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ MVP 原型验证      │    │ 核心补齐         │    │ 完整功能         │    │ 生产优化         │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ 2 个 Agent       │    │ +3 个 Agent      │    │ +2 个 Agent      │    │ 多模型路由       │
│ 基础框架          │    │ 规则引擎完善      │    │ 全部 7 个 Agent  │    │ AI 检测规避      │
│ 内容总监          │    │ 双层合规架构      │    │ 板块+地图API     │    │ 用户反馈闭环     │
│ 小红书文案        │    │ ChromaDB 知识库  │    │ 线索转化         │    │ CRM 集成         │
│ Streamlit UI      │    │ 素材模板库        │    │ 复盘分析         │    │ 自媒体发布       │
│ SQLite + 简单向量  │    │ 短视频编导        │    │ 政策科普转化     │    │ 语音输入         │
│ 基础违禁词规则     │    │ 合规质检 Agent    │    │ 成交案例素材化   │    │ 批量生成         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 13.2 Phase 1 - MVP 详细任务

| 任务 | 工时估计 | 责任人 | 交付物 |
|------|---------|-------|--------|
| 搭建项目骨架（目录结构/配置/依赖） | 0.5天 | 后端工程师 | 可运行的项目框架 |
| 实现 Agent 基类和 Skill 基类 | 1天 | 后端工程师 | agent_base.py, skill_base.py |
| 实现 Shared Context Bus | 0.5天 | 后端工程师 | context_bus.py |
| 实现 Task Manager（任务编排） | 1天 | 后端工程师 | task_manager.py |
| 实现内容总监 Agent + Prompt | 1天 | AI 工程师 | coordinator.py |
| 实现小红书文案 Agent + Prompt | 1.5天 | AI 工程师 | xiaohongshu_writer.py |
| 实现卖点分析师 Agent + Prompt | 0.5天 | AI 工程师 | property_analyst.py |
| 实现基础违禁词规则引擎 | 0.5天 | 后端工程师 | compliance_checker.py (Layer 1) |
| 搭建 SQLite 数据库 + 房源/小区表 | 0.5天 | 后端工程师 | 建表脚本 + 示例数据 |
| 搭建 Streamlit UI | 1.5天 | 前端工程师 | app.py (输入 → 生成 → 展示) |
| 端到端流程测试 | 1天 | QA | 测试用例 + 测试报告 |
| API 文档初版 | 0.5天 | 后端工程师 | Swagger UI |
| **总计** | **约 10 人天** | | |

### 13.3 关键里程碑

| 里程碑 | 时间 | 验收标准 |
|--------|------|---------|
| M1: 项目骨架搭建完成 | Day 1 | 项目可运行，基础 API 可访问 |
| M2: 单 Agent 可调用 | Day 3 | 输入房源信息，小红书笔记可生成 |
| M3: 完整链路跑通 | Day 5 | 输入小区名 → 卖点分析 → 笔记生成 → 合规检查 → 返回用户 |
| M4: MVP 可用 | Day 10 | 经纪人可通过 UI 完成内容生成全流程 |

---
## 14. 验收标准

### 14.1 Phase 1 MVP 验收条件

```
验收条件清单
├── ✅ 必选 (全部通过才能验收)
│   ├── AC-01: 经纪人输入 "写一篇 XX 小区的探房小红书" 后，系统在 3 分钟内返回完整笔记
│   ├── AC-02: 返回的笔记包含 标题 + 正文(>200字) + 标签(>5个) + emoji
│   ├── AC-03: 返回的内容经过合规检查，违禁词表命中时状态为 "warning" 或 "blocked"
│   ├── AC-04: 违禁词表可配置（新增/修改/删除）
│   ├── AC-05: 内容总监能正确识别 "小红书" "抖音" "视频" 等意图关键词
│   ├── AC-06: 卖点分析师能从房源资料中提取至少 3 个卖点和 1 个风险点
│   ├── AC-07: UI 能展示生成过程（任务进度）和最终结果
│   ├── AC-08: 同一房源第二次生成时，响应时间不超过第一次的 50%
│   └── AC-09: 5 套房源测试，至少 4 套生成的内容满足基本质量要求
│
├── 🟡 可选 (建议完成)
│   ├── AC-10: 支持语音输入（转文字后处理）
│   ├── AC-11: 生成内容可一键复制到剪贴板
│   └── AC-12: 支持历史记录查看和管理
│
└── 🔴 不可接受
    ├── 返回内容包含违禁词且未标记
    ├── 返回内容包含空白/无意义段落
    ├── 系统崩溃或卡死
    └── API 响应时间超过 5 分钟
```

### 14.2 测试用例（核心场景）

| TC ID | 场景 | 输入 | 预期输出 | 优先级 |
|-------|------|------|---------|--------|
| TC-01 | 正常探房笔记 | "帮我写一篇阳光城小区的探房小红书" | 标题+正文+标签+emoji，合规通过 | P0 |
| TC-02 | 含违禁词输入 | "这个小区升值潜力巨大" | 合规报告显示"升值"违禁词，状态=blocked | P0 |
| TC-03 | 学区承诺检测 | "对口XX名校" | 合规报告提示学区风险，状态=warning | P0 |
| TC-04 | 空输入处理 | (空) | 提示 "请输入小区名称或房源信息" | P1 |
| TC-05 | 无资料房源 | "帮我写一个不存在的房源" | 提示 "未找到相关房源信息，请手动输入描述" | P1 |
| TC-06 | 多平台识别 | "想拍个视频脚本" | 内容总监路由到短视频编导 Agent | P1 |
| TC-07 | 并发请求 | 同时 3 个经纪人请求 | 全部在 5 分钟内返回，无错误 | P2 |
| TC-08 | 违禁词表更新 | 新增违禁词后重新检查已有内容 | 新词命中时正确标记 | P1 |

### 14.3 上线前检查清单

```
□ 所有 P0 测试用例通过
□ 违禁词表已配置并审核
□ Agent Prompt 已配置（至少 内容总监 + 小红书文案 + 卖点分析）
□ API 文档已生成
□ 数据库建表脚本已执行
□ 部署文档已编写
□ 用户手册初版已完成
□ 至少 5 套房源测试数据已入库
□ 合规检查不可用的情况下系统应禁止发布（fail-safe）
```
