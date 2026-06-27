# 🏠 房地产销售 Agent 智能体

AI 驱动的房地产内容生成平台，帮助房产经纪人快速产出合规、高质量的多平台内容。

## 📋 项目概述

本项目基于 LangGraph 多 Agent 架构，实现从房源信息到多平台内容（小红书笔记、短视频脚本、客户话术等）的全流程自动化生成，并内置合规审查机制，确保内容符合《广告法》和房地产广告发布规定。

## 🎯 核心功能

- **内容生成**：一键生成小红书笔记、短视频脚本、客户话术
- **合规审查**：内置违禁词规则引擎，自动拦截违规内容
- **多 Agent 协作**：内容总监编排 6 个专业 Agent 协同工作
- **知识库支持**：房源、板块、政策、模板、案例 5 大知识库
- **多平台适配**：支持抖音、小红书、朋友圈、企微 4 个平台

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面                              │
│              (Streamlit UI / FastAPI API)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      内容总监 Agent                          │
│              (任务分析 + 流程编排)                            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 卖点分析师   │    │ 小红书文案   │    │ 短视频编导   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    合规规则引擎                              │
│              (违禁词检查 + 风险评级)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据存储层                                │
│         (SQLite + ChromaDB 向量库)                           │
└─────────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
real-estate-agent/
├── agent/                          # Agent 核心代码
│   ├── coordinator.py              # 🎯 内容总监 Agent
│   ├── property_analyst.py         # 🔍 卖点分析师 Agent
│   └── xiaohongshu_writer.py       # ✍️ 小红书文案 Agent
│
├── core/                           # 框架核心
│   ├── agent_base.py               # Agent 基类
│   ├── skill_base.py               # Skill 基类
│   ├── task_manager.py             # 任务管理与编排
│   ├── context_bus.py              # Shared Context Bus
│   └── model_router.py             # 多模型路由
│
├── skills/                         # Skill 实现
│   ├── selling_point_extractor.py  # SK-01 卖点提炼
│   ├── script_generator.py         # SK-02 脚本生成
│   ├── note_writer.py              # SK-03 笔记撰写
│   ├── topic_planner.py            # SK-04 选题策划
│   ├── talk_generator.py           # SK-05 话术生成
│   ├── compliance_checker.py       # SK-06 合规检查
│   ├── review_analyzer.py          # SK-07 复盘分析
│   ├── policy_converter.py         # SK-08 政策科普转化
│   └── case_to_template.py         # SK-09 成交案例素材化
│
├── compliance/                     # 合规模块
│   └── rule_engine.py              # 违禁词规则引擎
│
├── knowledge/                      # 知识库
│   └── banned_words.py             # 违禁词表
│
├── database/                       # 数据库
│   └── models.py                   # SQLAlchemy 模型
│
├── api/                            # API 接口
│   ├── main.py                     # FastAPI 入口
│   └── routes/
│       └── content.py              # 内容生成接口
│
├── web/                            # 前端
│   └── app.py                      # Streamlit UI
│
├── config/                         # 配置
│   ├── prompts/                    # Agent Prompt 模板
│   ├── banned_words.json           # 违禁词列表
│   └── settings.py                 # 环境配置
│
├── tests/                          # 测试
│   └── test_workflow.py            # 端到端测试
│
├── requirements.txt                # Python 依赖
└── docker-compose.yml              # Docker 部署
```

## 🚀 快速开始

### 1. 环境要求

- Python >= 3.10
- DeepSeek API Key 或 OpenAI API Key

### 2. 安装依赖

```bash
cd real-estate-agent
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 使用 DeepSeek V3（推荐）
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# 或使用 OpenAI GPT-4o
export OPENAI_API_KEY="your-openai-api-key"
```

### 4. 启动 Streamlit UI

```bash
streamlit run web/app.py
```

访问 http://localhost:8501 即可使用。

### 5. 启动 FastAPI API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

### 6. Docker 部署

```bash
docker-compose up -d
```

## 📖 API 文档

启动 FastAPI 后，访问 http://localhost:8000/docs 查看交互式 API 文档。

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/content/generate` | POST | 生成内容 |
| `/api/content/compliance/check` | POST | 合规检查 |
| `/api/content/lead/convert` | POST | 线索转化 |
| `/api/content/topic/plan` | POST | 选题策划 |
| `/api/system/status` | GET | 系统状态 |

## 🧪 运行测试

```bash
python tests/test_workflow.py
```

## 📊 性能指标

| 指标 | 目标值 |
|------|--------|
| 内容生成耗时 | < 3 分钟 |
| 合规违规率 | < 1% |
| 单次调用成本 | < ¥0.05（DeepSeek V3） |

## 📝 开发计划

### Phase 1 (已完成)
- ✅ 项目框架搭建
- ✅ 3 个核心 Agent（内容总监、卖点分析师、小红书文案）
- ✅ 9 个 Skill 实现
- ✅ 违禁词规则引擎
- ✅ SQLite 数据库
- ✅ Streamlit UI
- ✅ FastAPI API

### Phase 2 (计划中)
- 🔲 短视频编导 Agent
- 🔲 板块研究员 Agent
- 🔲 ChromaDB 向量库
- 🔲 素材模板库
- 🔲 双层合规架构

### Phase 3 (计划中)
- 🔲 线索转化 Agent
- 🔲 复盘分析 Agent
- 🔲 政策科普转化 Agent
- 🔲 完整功能集成

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- 项目地址：[GitHub](https://github.com/your-org/real-estate-agent)
- 文档：[PRD.md](./PRD.md) | [ARCHITECTURE.md](./ARCHITECTURE.md)
