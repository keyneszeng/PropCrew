"""
Streamlit UI - Phase 3 完整功能版

房地产销售 Agent 智能体的用户界面。
支持全功能：内容生成、线索转化、复盘分析、政策科普、合规检查等。
"""

import streamlit as st
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

# 导入核心模块
from core.context_bus import ContextBus
from core.task_manager import TaskManager, TaskPriority
from core.model_router import ModelRouter, ModelConfig
from agent.coordinator import ContentCoordinatorAgent
from agent.property_analyst import PropertyAnalystAgent
from agent.xiaohongshu_writer import XiaohongshuWriterAgent
from agent.video_director import VideoDirectorAgent
from agent.district_researcher import DistrictResearcherAgent
from agent.lead_converter import LeadConverterAgent
from agent.compliance_officer import ComplianceOfficerAgent
from agent.review_analysis import ReviewAnalysisAgent
from agent.policy_converter_agent import PolicyConverterAgent
from compliance.rule_engine import ComplianceRuleEngine
from compliance.ai_checker import AIComplianceChecker
from knowledge.banned_words import BannedWords
from database.models import DatabaseManager, Property, Post, Lead


# 页面配置
st.set_page_config(
    page_title="房产 Agent 智能体",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ====== 初始化会话状态 ======
if "context_bus" not in st.session_state:
    st.session_state.context_bus = ContextBus()
if "task_manager" not in st.session_state:
    st.session_state.task_manager = TaskManager()
if "model_router" not in st.session_state:
    st.session_state.model_router = ModelRouter()
if "agents" not in st.session_state:
    st.session_state.agents = {}
if "compliance_engine" not in st.session_state:
    st.session_state.compliance_engine = ComplianceRuleEngine()
if "ai_checker" not in st.session_state:
    st.session_state.ai_checker = None
if "db_manager" not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if "history" not in st.session_state:
    st.session_state.history = []
if "leads" not in st.session_state:
    st.session_state.leads = []
if "model_configured" not in st.session_state:
    st.session_state.model_configured = False


# ====== 初始化 Agent ======
def init_agents():
    """初始化所有 Agent（Phase 1-3）"""
    if st.session_state.agents:
        return
    
    router = st.session_state.model_router
    context_bus = st.session_state.context_bus
    task_manager = st.session_state.task_manager
    
    # Phase 1/2
    coordinator = ContentCoordinatorAgent(model_router=router)
    coordinator.set_context_bus(context_bus)
    task_manager.register_agent(coordinator.agent_id, coordinator)
    
    analyst = PropertyAnalystAgent(model_router=router)
    analyst.set_context_bus(context_bus)
    task_manager.register_agent(analyst.agent_id, analyst)
    
    writer = XiaohongshuWriterAgent(model_router=router)
    writer.set_context_bus(context_bus)
    task_manager.register_agent(writer.agent_id, writer)
    
    video_dir = VideoDirectorAgent(model_router=router)
    video_dir.set_context_bus(context_bus)
    task_manager.register_agent(video_dir.agent_id, video_dir)
    
    district_researcher = DistrictResearcherAgent(model_router=router)
    district_researcher.set_context_bus(context_bus)
    task_manager.register_agent(district_researcher.agent_id, district_researcher)
    
    # Phase 3
    lead_converter = LeadConverterAgent(model_router=router)
    lead_converter.set_context_bus(context_bus)
    task_manager.register_agent(lead_converter.agent_id, lead_converter)
    
    review_analyst = ReviewAnalysisAgent(model_router=router)
    review_analyst.set_context_bus(context_bus)
    task_manager.register_agent(review_analyst.agent_id, review_analyst)
    
    policy_converter = PolicyConverterAgent(model_router=router)
    policy_converter.set_context_bus(context_bus)
    task_manager.register_agent(policy_converter.agent_id, policy_converter)
    
    compliance_officer = ComplianceOfficerAgent(model_router=router)
    compliance_officer.set_context_bus(context_bus)
    task_manager.register_agent(compliance_officer.agent_id, compliance_officer)
    
    # 初始化 AI Checker
    st.session_state.ai_checker = AIComplianceChecker(model_router=router)
    
    st.session_state.agents = {
        "coordinator": coordinator,
        "analyst": analyst,
        "writer": writer,
        "video_director": video_dir,
        "district_researcher": district_researcher,
        "lead_converter": lead_converter,
        "review_analyst": review_analyst,
        "policy_converter": policy_converter,
        "compliance_officer": compliance_officer,
    }


# ====== 侧边栏 ======
with st.sidebar:
    st.title("🏠 房产 Agent")
    st.caption("Phase 3 | 9 Agents · 9 Skills")
    st.markdown("---")
    
    # 模型配置
    st.subheader("🔧 模型配置")
    model_choice = st.selectbox(
        "选择模型",
        ["deepseek-v3", "gpt-4o"],
        help="选择用于内容生成的 LLM 模型"
    )
    
    api_key = st.text_input(
        "API Key",
        type="password",
        help="输入 LLM API Key"
    )
    
    if api_key and not st.session_state.model_configured:
        if model_choice == "deepseek-v3":
            config = ModelConfig(
                provider="deepseek",
                model_name="deepseek-chat",
                api_key=api_key,
            )
        else:
            config = ModelConfig(
                provider="openai",
                model_name="gpt-4o",
                api_key=api_key,
            )
        st.session_state.model_router.register_model(config)
        st.session_state.model_configured = True
        init_agents()
        st.success(f"✅ {model_choice} 已配置，9 个 Agent 就绪")
    
    if st.session_state.model_configured:
        st.info(f"✅ 模型已配置 | {len(st.session_state.agents)} 个 Agent")
    
    st.markdown("---")
    
    # 功能菜单
    st.subheader("📋 功能菜单")
    menu = st.radio(
        "选择功能",
        [
            "📝 生成内容",
            "💬 线索转化",
            "📊 复盘分析",
            "📋 政策科普",
            "🔍 合规检查",
            "📋 线索管理",
            "📊 历史记录",
            "📦 批量生成",
            "💬 用户反馈",
            "⚙️ 系统状态",
        ],
        index=0,
    )
    
    st.markdown("---")
    st.markdown("### 📖 快速指南")
    st.markdown("""
    1. **生成内容** → 小红书笔记/短视频脚本
    2. **线索转化** → 客户话术生成
    3. **复盘分析** → 数据复盘+选题推荐
    4. **政策科普** → 新政解读
    5. **合规检查** → 双层合规检查
    """)


# ====== 主内容区域 ======
st.title("🏠 房产销售 Agent 智能体")
st.markdown("Phase 3 完整功能版 · 9 个 Agent 协同工作")
st.markdown("---")


# ====== 功能 1: 生成内容 ======
if menu == "📝 生成内容":
    st.subheader("📝 内容生成")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        platform = st.selectbox("选择平台", ["xiaohongshu", "douyin"], format_func=lambda x: {"xiaohongshu": "小红书", "douyin": "抖音"}[x])
        content_type = st.selectbox("内容类型", ["note", "script"], format_func=lambda x: {"note": "笔记", "script": "脚本"}[x])
        
        st.markdown("### 📋 房源信息")
        property_info = st.text_area(
            "请输入房源信息",
            placeholder="地址：XX小区\n户型：3室2厅2卫\n面积：120平米\n价格：800万\n特色：南北通透，精装修",
            height=200,
        )
        
        template = st.selectbox("快速模板", ["自定义", "刚需首套", "改善换房", "学区房"])
        if template != "自定义":
            templates = {
                "刚需首套": "地址：XX小区\n户型：2室1厅1卫\n面积：80平米\n价格：300万\n特色：首付低，交通便利",
                "改善换房": "地址：XX小区\n户型：3室2厅2卫\n面积：120平米\n价格：600万\n特色：南北通透，精装修",
                "学区房": "地址：XX小区\n户型：2室2厅1卫\n面积：90平米\n价格：500万\n特色：对口名校，教育资源丰富",
            }
            property_info = st.text_area("房源信息", value=templates[template], height=200)
    
    with col2:
        st.markdown("### ⚙️ 选项")
        word_count = st.slider("字数", 200, 800, 400)
        include_tags = st.checkbox("包含标签", True)
        include_emoji = st.checkbox("包含 Emoji", True)
    
    if st.button("🚀 生成", type="primary", use_container_width=True):
        if not property_info.strip():
            st.error("请输入房源信息")
        elif not st.session_state.model_configured:
            st.error("请先配置 API Key")
        else:
            with st.spinner("🤖 正在生成..."):
                try:
                    agents = st.session_state.agents
                    context_bus = st.session_state.context_bus
                    context_bus.clear()
                    
                    # 卖点分析
                    st.info("🔍 卖点分析中...")
                    analyst_result = asyncio.run(agents["analyst"].execute({"property_info": property_info}))
                    
                    # 内容生成
                    st.info(f"✍️ {'小红书文案' if platform == 'xiaohongshu' else '短视频编导'} 创作中...")
                    if platform == "xiaohongshu":
                        writer_result = asyncio.run(agents["writer"].execute({
                            "property_info": property_info,
                            "selling_points": json.loads(analyst_result.content).get("selling_points", []),
                        }))
                    else:
                        writer_result = asyncio.run(agents["video_director"].execute({
                            "property_info": property_info,
                            "selling_points": json.loads(analyst_result.content).get("selling_points", []),
                        }))
                    
                    content = json.loads(writer_result.content)
                    
                    # 合规检查
                    st.info("🔍 合规检查中...")
                    full_text = f"{content.get('title', '')} {content.get('content', '')} {content.get('text', '')}"
                    compliance_result = asyncio.run(agents["compliance_officer"].execute({
                        "text": full_text, "platform": platform
                    }))
                    compliance_report = json.loads(compliance_result.content)
                    
                    # 显示
                    st.success("✅ 生成完成！")
                    
                    tab1, tab2, tab3 = st.tabs(["📝 内容预览", "🔍 合规报告", "📊 卖点分析"])
                    
                    with tab1:
                        st.markdown(f"### {content.get('title', '')}")
                        st.markdown(content.get('content', ''))
                        if content.get('tags'):
                            st.markdown(f"标签：{' '.join(['#'+t for t in content.get('tags', [])])}")
                        if content.get('scenes'):
                            for scene in content.get('scenes', []):
                                st.markdown(f"**第{scene.get('scene_number')}镜** ({scene.get('duration','')}s): {scene.get('content','')}")
                        st.markdown(f"---\n**合规评分**: {compliance_report.get('compliance_score', 0)}")
                    
                    with tab2:
                        status = compliance_report.get('status', 'pass')
                        if status == 'pass':
                            st.success("✅ 合规通过")
                        elif status == 'warning':
                            st.warning(f"⚠️ 合规警告 (评分: {compliance_report.get('compliance_score', 0)})")
                        else:
                            st.error(f"🔴 合规拦截 (评分: {compliance_report.get('compliance_score', 0)})")
                        
                        # 修改建议
                        for s in compliance_report.get('modification_suggestions', []):
                            st.info(f"🔄 {s.get('original','')} → **{s.get('suggested','')}**")
                    
                    with tab3:
                        analyst_data = json.loads(analyst_result.content)
                        for sp in analyst_data.get('selling_points', []):
                            st.success(f"**{sp.get('category','')}**: {sp.get('point','')}")
                    
                    st.session_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "content",
                        "platform": platform,
                        "content": content,
                        "compliance": compliance_report,
                    })
                    
                except Exception as e:
                    st.error(f"❌ 生成失败: {e}")


# ====== 功能 2: 线索转化 ======
elif menu == "💬 线索转化":
    st.subheader("💬 线索转化 - 话术生成")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        scenario = st.selectbox(
            "场景",
            ["comment_reply", "private_message", "phone_call", "visit_invitation", "objection_handling", "closing"],
            format_func=lambda x: {
                "comment_reply": "💬 评论回复", "private_message": "✉️ 私信跟进",
                "phone_call": "📞 电话邀约", "visit_invitation": "🏠 看房邀请",
                "objection_handling": "🤔 异议处理", "closing": "✍️ 逼定话术",
            }[x]
        )
        
        customer_question = st.text_area(
            "客户问题/留言",
            placeholder="客户说：这套房子价格还能再低吗？",
            height=120,
        )
        
        customer_profile = st.text_area(
            "客户画像（可选）",
            placeholder="预算500-600万，三口之家，重点关注学区",
            height=80,
        )
    
    with col2:
        st.markdown("### 快速场景")
        quick_questions = {
            "价格咨询": "这套房子价格还能再低吗？",
            "学区咨询": "这个小区对口什么学校？",
            "看房需求": "什么时候可以看房？",
            "比价对比": "我看隔壁小区更便宜",
        }
        for label, question in quick_questions.items():
            if st.button(label, use_container_width=True):
                customer_question = question
    
    if st.button("🚀 生成话术", type="primary", use_container_width=True):
        if not customer_question.strip():
            st.error("请输入客户问题")
        elif not st.session_state.model_configured:
            st.error("请先配置 API Key")
        else:
            with st.spinner("🤔 分析客户意图并生成话术..."):
                try:
                    result = asyncio.run(st.session_state.agents["lead_converter"].execute({
                        "customer_question": customer_question,
                        "customer_profile": {"description": customer_profile} if customer_profile else {},
                        "scenario": scenario,
                    }))
                    
                    data = json.loads(result.content)
                    
                    st.success("✅ 话术生成完成")
                    
                    # 意图分析
                    intent = data.get("intent_analysis", {})
                    st.info(f"📊 意图识别: {intent.get('intent_type', 'general')} | 兴趣度: {'★' * intent.get('intensity', 3) + '☆' * (5 - intent.get('intensity', 3))}")
                    
                    # 话术选项
                    st.markdown("### 💬 推荐话术")
                    recommended = data.get("recommended_option", 1)
                    for opt in data.get("options", []):
                        with st.expander(f"{'⭐ ' if opt.get('id') == recommended else ''}{opt.get('style','通用')}方案", expanded=opt.get('id') == recommended):
                            st.markdown(opt.get('text', ''))
                            st.caption(f"亮点: {', '.join(opt.get('key_highlights', []))}")
                            st.caption(f"引导动作: {opt.get('call_to_action', '')}")
                    
                    # 合规提示
                    for note in data.get("compliance_notes", []):
                        st.warning(f"⚠️ {note}")
                    
                    st.session_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "lead",
                        "scenario": scenario,
                        "question": customer_question,
                        "result": data,
                    })
                    
                except Exception as e:
                    st.error(f"❌ 生成失败: {e}")


# ====== 功能 3: 复盘分析 ======
elif menu == "📊 复盘分析":
    st.subheader("📊 复盘分析 & 选题推荐")
    
    st.markdown("### 📋 发布数据输入")
    col1, col2 = st.columns(2)
    
    with col1:
        total_posts = st.number_input("总发布数", 0, 100, 10)
        total_views = st.number_input("总曝光", 0, 100000, 5000)
    
    with col2:
        total_likes = st.number_input("总点赞", 0, 10000, 500)
        total_comments = st.number_input("总评论", 0, 5000, 200)
    
    feedack_text = st.text_area("经纪人反馈（可选）", placeholder="经纪人觉得什么类型的内容效果最好？有什么改进建议？", height=80)
    
    if st.button("📊 开始复盘分析", type="primary", use_container_width=True):
        if not st.session_state.model_configured:
            st.error("请先配置 API Key")
        else:
            with st.spinner("📊 分析中..."):
                try:
                    publish_records = [
                        {"views": total_views // total_posts if total_posts > 0 else 0,
                         "likes": total_likes // total_posts if total_posts > 0 else 0,
                         "comments": total_comments // total_posts if total_posts > 0 else 0,
                         "title": f"内容{i+1}", "platform": "xiaohongshu"}
                        for i in range(total_posts)
                    ] if total_posts > 0 else []
                    
                    result = asyncio.run(st.session_state.agents["review_analyst"].execute({
                        "publish_records": publish_records,
                        "engagement_data": {"total_views": total_views, "total_likes": total_likes, "total_comments": total_comments},
                        "user_feedback": [{"content": feedack_text}] if feedack_text else [],
                    }))
                    
                    data = json.loads(result.content)
                    
                    st.success("✅ 复盘分析完成")
                    
                    tab1, tab2, tab3 = st.tabs(["📊 数据概览", "💡 洞察建议", "📅 下周选题"])
                    
                    with tab1:
                        metrics = data.get("metrics", {})
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("总发布", metrics.get("total_posts", 0))
                        c2.metric("总曝光", metrics.get("total_views", 0))
                        c3.metric("平均曝光/条", f"{metrics.get('avg_views_per_post', 0):.0f}")
                        c4.metric("最佳平台", metrics.get("best_platform", "-"))
                        st.markdown(f"**总结**: {data.get('summary', '')}")
                    
                    with tab2:
                        for insight in data.get("insights", []):
                            icon = {"success": "✅", "improvement": "📈", "risk": "⚠️"}.get(insight.get('type', ''), "💡")
                            st.info(f"{icon} {insight.get('content', '')}")
                    
                    with tab3:
                        weekly = data.get("weekly_plan", {})
                        for day, plan in weekly.items():
                            st.markdown(f"**{day.upper()}**: {plan.get('theme', '-')} ({plan.get('platform','-')} · {plan.get('content_type','-')})")
                    
                except Exception as e:
                    st.error(f"❌ 分析失败: {e}")


# ====== 功能 4: 政策科普 ======
elif menu == "📋 政策科普":
    st.subheader("📋 政策科普内容生成")
    
    policy_title = st.text_input("政策标题", placeholder="如：最新公积金贷款政策调整")
    policy_text = st.text_area("政策原文", placeholder="粘贴政策原文...", height=200)
    
    target = st.selectbox("目标受众", ["general", "buyer", "seller", "investor"],
                          format_func=lambda x: {"general": "通用", "buyer": "购房者", "seller": "业主/卖房者", "investor": "投资者"}[x])
    
    if st.button("📋 生成科普内容", type="primary", use_container_width=True):
        if not st.session_state.model_configured:
            st.error("请先配置 API Key")
        elif not policy_text:
            st.error("请提供政策原文")
        else:
            with st.spinner("📋 政策解读中..."):
                try:
                    result = asyncio.run(st.session_state.agents["policy_converter"].execute({
                        "policy_text": policy_text,
                        "policy_title": policy_title,
                        "target_audience": target,
                    }))
                    
                    data = json.loads(result.content)
                    st.success("✅ 政策解读完成")
                    
                    tab1, tab2, tab3 = st.tabs(["📝 通俗解读", "📊 影响分析", "📋 输出方案"])
                    
                    with tab1:
                        st.markdown(f"### {data.get('policy_info', {}).get('title', '政策解读')}")
                        st.info(data.get('plain_explanation', ''))
                        st.markdown("---")
                        st.markdown(data.get('detailed_explanation', ''))
                    
                    with tab2:
                        for impact in data.get("impact_analysis", []):
                            icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(impact.get('severity', '中'), "⚪")
                            st.markdown(f"{icon} **{impact.get('group','')}**: {impact.get('impact','')}")

                    with tab3:
                        for plan in data.get("output_plans", []):
                            platform_icon = {"xiaohongshu": "📕", "douyin": "🎵", "wechat": "💬"}.get(plan.get('platform',''), "📄")
                            st.success(f"{platform_icon} **{plan.get('title','')}** ({plan.get('content_type','')})")
                            for kp in plan.get("key_points", []):
                                st.markdown(f"  - {kp}")

                except Exception as e:
                    st.error(f"❌ 解读失败: {e}")


# ====== 功能 5: 合规检查 ======
elif menu == "🔍 合规检查":
    st.subheader("🔍 双层合规检查")
    st.markdown("**Layer 1**: 规则引擎 · **Layer 2**: AI 语义检查")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        check_text = st.text_area("输入要检查的内容", placeholder="粘贴文案内容...", height=200)
    
    with col2:
        check_platform = st.selectbox("发布平台", ["xiaohongshu", "douyin", "wechat"])
    
    if st.button("🔍 检查合规性", type="primary", use_container_width=True):
        if not check_text.strip():
            st.error("请输入内容")
        elif not st.session_state.model_configured:
            # 只用规则引擎
            result = st.session_state.compliance_engine.check(check_text)
            if result.is_compliant:
                st.success("✅ 合规通过 (规则引擎)")
            else:
                st.warning(f"⚠️ 发现 {len(result.violations)} 个问题")
                for v in result.violations:
                    st.error(f"- {v.get('word', v.get('match',''))}: {v.get('suggestion','')}")
        else:
            with st.spinner("🔍 双层检查中..."):
                try:
                    result = asyncio.run(st.session_state.agents["compliance_officer"].execute({
                        "text": check_text,
                        "platform": check_platform,
                    }))
                    
                    data = json.loads(result.content)
                    
                    status = data.get("status", "pass")
                    score = data.get("compliance_score", 100)
                    
                    if status == "pass":
                        st.success(f"✅ 合规通过 (评分: {score})")
                    elif status == "warning":
                        st.warning(f"⚠️ 合规警告 (评分: {score})")
                    else:
                        st.error(f"🔴 合规拦截 (评分: {score})")
                    
                    st.markdown(f"**{data.get('summary','')}**")
                    
                    # Layer 1 结果
                    layer1 = data.get("layer1_results", {})
                    if layer1.get("rule_matches"):
                        st.markdown("### Layer 1: 规则引擎匹配")
                        for m in layer1.get("rule_matches", []):
                            st.error(f"🔴 [{m.get('severity','')}] {m.get('word', m.get('match',''))} → {m.get('suggestion','')}")
                    
                    # Layer 2 结果
                    layer2 = data.get("layer2_results", {})
                    if layer2.get("ai_concerns"):
                        st.markdown("### Layer 2: AI 语义风险")
                        for c in layer2.get("ai_concerns", []):
                            st.warning(f"🟡 {c.get('text','')}: {c.get('reason','')}")
                    
                    # 修改建议
                    if data.get("modification_suggestions"):
                        st.markdown("### 💡 修改建议")
                        for s in data.get("modification_suggestions", []):
                            st.info(f"🔄 {s.get('original','')} → **{s.get('suggested','')}** ({s.get('reason','')})")
                    
                except Exception as e:
                    st.error(f"❌ 检查失败: {e}")


# ====== 功能 6: 线索管理 ======
elif menu == "📋 线索管理":
    st.subheader("📋 客户线索管理")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 新增线索")
        lead_source = st.selectbox("来源", ["xiaohongshu", "douyin", "wechat", "phone", "referral"])
        lead_name = st.text_input("客户名称")
        lead_phone = st.text_input("联系方式")
        lead_note = st.text_area("备注")
        
        if st.button("➕ 添加线索", use_container_width=True):
            lead = {
                "id": len(st.session_state.leads) + 1,
                "source": lead_source,
                "name": lead_name,
                "phone": lead_phone,
                "note": lead_note,
                "status": "pending",
                "intention": 3,
                "created_at": datetime.now().isoformat()[:19],
            }
            st.session_state.leads.append(lead)
            st.success("✅ 线索已添加")
    
    with col2:
        st.markdown("### 线索列表")
        status_filter = st.selectbox("筛选状态", ["all", "pending", "contacted", "invited", "visited", "closed", "lost"],
                                     format_func=lambda x: {"all": "全部", "pending": "待跟进", "contacted": "已联系",
                                        "invited": "已邀约", "visited": "已带看", "closed": "已成交", "lost": "已流失"}[x])
        
        leads_to_show = st.session_state.leads
        if status_filter != "all":
            leads_to_show = [l for l in leads_to_show if l["status"] == status_filter]
        
        if not leads_to_show:
            st.info("暂无线索")
        else:
            for lead in leads_to_show:
                with st.expander(f"{'📌' if lead['intention'] >= 4 else '📎'} {lead.get('name','未知')} | {lead.get('source','')} | {lead.get('status','')}"):
                    st.markdown(f"**来源**: {lead.get('source','')}")
                    st.markdown(f"**联系方式**: {lead.get('phone','')}")
                    st.markdown(f"**备注**: {lead.get('note','无')}")
                    st.markdown(f"**意向度**: {'★' * lead.get('intention', 3) + '☆' * (5 - lead.get('intention', 3))}")
                    
                    new_status = st.selectbox(
                        "更新状态",
                        ["pending", "contacted", "invited", "visited", "closed", "lost"],
                        index=["pending", "contacted", "invited", "visited", "closed", "lost"].index(lead["status"]),
                        key=f"status_{lead['id']}",
                    )
                    if new_status != lead["status"]:
                        lead["status"] = new_status
                        st.success("状态已更新")


# ====== 功能 7: 历史记录 ======
elif menu == "📊 历史记录":
    st.subheader("📊 历史记录")
    
    if not st.session_state.history:
        st.info("暂无历史记录")
    else:
        type_filter = st.selectbox("筛选类型", ["all", "content", "lead", "policy"],
                                   format_func=lambda x: {"all": "全部", "content": "内容生成", "lead": "线索转化", "policy": "政策科普"}[x])
        
        for i, record in enumerate(reversed(st.session_state.history)):
            rtype = record.get("type", "content")
            if type_filter != "all" and rtype != type_filter:
                continue
            
            with st.expander(f"{'📝' if rtype == 'content' else '💬' if rtype == 'lead' else '📋'} 记录 {len(st.session_state.history) - i} - {record['timestamp'][:19]}"):
                st.json(record)


# ====== 功能 8: 系统状态 ======


# ====== 功能: 批量生成 ======
elif menu == "📦 批量生成":
    st.subheader("📦 批量内容生成")
    st.markdown("一次输入多套房源，批量生成多平台内容")
    
    with st.form("batch_form"):
        st.markdown("### 🏠 房源列表（每行一条）")
        properties_text = st.text_area(
            "输入房源（格式：标题|户型|面积|价格|亮点）",
            placeholder="阳光城|3室2厅|120|800|南北通透\n翡翠湾|2室1厅|85|500|临湖景观\n紫金府|4室2厅|150|1200|核心地段",
            height=120,
        )
        
        col1, col2 = st.columns(2)
        with col1:
            platforms = st.multiselect("选择平台", ["xiaohongshu", "douyin", "wechat", "weibo"],
                                       default=["xiaohongshu", "douyin"])
        with col2:
            content_types = st.multiselect("内容类型", ["note", "script", "article"],
                                           default=["note", "script"])
        
        submitted = st.form_submit_button("🚀 批量生成", type="primary", use_container_width=True)
    
    if submitted and properties_text.strip():
        if not st.session_state.model_configured:
            st.error("请先配置 API Key")
        else:
            properties = []
            for line in properties_text.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 1:
                    properties.append({
                        "title": parts[0].strip(),
                        "rooms": parts[1].strip() if len(parts) > 1 else "",
                        "area": parts[2].strip() if len(parts) > 2 else "",
                        "price": parts[3].strip() if len(parts) > 3 else "",
                        "highlight": parts[4].strip() if len(parts) > 4 else "",
                    })
            
            with st.spinner(f"📦 正在生成 {len(properties) * len(platforms) * len(content_types)} 条内容..."):
                from skills.batch_generator import BatchGenerator
                bg = BatchGenerator(model_router=st.session_state.model_router)
                result = asyncio.run(bg.execute({
                    "properties": properties,
                    "platforms": platforms,
                    "content_types": content_types,
                }))
                
                if result.success:
                    summary = result.output["summary"]
                    st.success(f"✅ 生成完成！成功 {summary['completed']} / 总数 {summary['total']}")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("总计", summary["total"])
                    col2.metric("成功", summary["completed"])
                    col3.metric("失败", summary["failed"])
                    
                    st.markdown("### 📋 生成结果")
                    for res in result.output["results"]:
                        icon = "✅" if res.get("success") else "❌"
                        st.markdown(f"{icon} **{res.get('property','')}** → {res.get('platform','')} ({res.get('content_type','')})")
                        if res.get("title"):
                            st.caption(f"  标题: {res.get('title','')}")
                    
                    st.session_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "batch",
                        "summary": summary,
                        "results": result.output["results"],
                    })


# ====== 功能: 用户反馈 ======
elif menu == "💬 用户反馈":
    st.subheader("💬 用户反馈 & Prompt 优化")
    st.markdown("帮助系统持续改进内容质量")
    
    tab1, tab2 = st.tabs(["📝 提交反馈", "📊 反馈统计"])
    
    with tab1:
        st.markdown("### 对生成内容的评价")
        
        agent_options = {
            "coordinator": "内容总监",
            "xiaohongshu_writer": "小红书文案",
            "video_director": "短视频编导",
            "lead_converter": "线索转化顾问",
            "policy_converter": "政策科普顾问",
            "compliance_officer": "合规质检员",
        }
        
        col1, col2 = st.columns(2)
        with col1:
            fb_agent = st.selectbox("选择 Agent", list(agent_options.keys()),
                                    format_func=lambda x: agent_options.get(x, x))
        with col2:
            fb_score = st.slider("评分", 1, 5, 4, help="1=很差, 5=非常好")
        
        fb_good = st.text_area("做得好的地方", placeholder="内容准确、风格合适...", height=80)
        fb_improve = st.text_area("需要改进的地方", placeholder="分行太密、关键词过多...", height=80)
        
        if st.button("💬 提交反馈", type="primary", use_container_width=True):
            from skills.feedback_collector import FeedbackCollector
            fc = FeedbackCollector(model_router=st.session_state.model_router)
            result = asyncio.run(fc.execute({
                "feedback_data": {
                    "agent_name": fb_agent,
                    "score": fb_score,
                    "needs_improvement": [fb_improve] if fb_improve else [],
                    "good_points": [fb_good] if fb_good else [],
                }
            }))
            
            if result.success:
                st.success("✅ 反馈已提交，感谢您的意见！")
                if result.output.get("optimization_suggestions"):
                    st.markdown("### 💡 系统优化建议")
                    for s in result.output["optimization_suggestions"]:
                        st.info(s)
                    
                    st.session_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "feedback",
                        "agent": fb_agent,
                        "score": fb_score,
                    })
    
    with tab2:
        st.markdown("### 📊 反馈统计")
        fc = FeedbackCollector()
        stats = fc.get_stats()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("总反馈数", stats["total"])
        col2.metric("平均评分", f"{stats['avg_score']:.1f}" if stats['total'] > 0 else "-")
        col3.metric("好评率", f"{stats['high_scores'] / max(stats['total'],1) * 100:.0f}%" if stats['total'] > 0 else "-")
        
        st.caption("提示：反馈数据保存在内存中，重启后会重置。生产环境应持久化存储。")


