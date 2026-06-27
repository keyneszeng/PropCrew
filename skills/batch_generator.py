"""
SK-10: 批量内容生成 Skill

一次输入多套房源，批量生成不同平台的不同类型内容。
支持并行处理和渐进式显示。
"""

from typing import Any, Dict, List, Optional
from core.skill_base import BaseSkill, SkillResult
import logging
import asyncio

logger = logging.getLogger(__name__)


class BatchGenerator(BaseSkill):
    """SK-10: 批量内容生成 Skill"""

    def __init__(self, model_router=None):
        super().__init__(
            skill_id="SK-10",
            name="批量内容生成",
            description="一次输入多套房源，批量生成不同平台/类型的内容",
            input_schema={
                "properties": {"required": True, "type": "list"},
                "platforms": {"required": False, "type": "list"},
                "content_types": {"required": False, "type": "list"},
                "progress_callback": {"required": False, "type": "function"},
            },
            output_schema={
                "batch_id": {"type": "str"},
                "results": {"type": "list"},
                "summary": {"type": "dict"},
            },
        )
        self.model_router = model_router

    async def execute(self, input_data: Dict[str, Any]) -> SkillResult:
        """执行批量内容生成"""
        try:
            properties = input_data.get("properties", [])
            platforms = input_data.get("platforms", ["xiaohongshu"])
            content_types = input_data.get("content_types", ["note"])
            progress_cb = input_data.get("progress_callback")

            if not properties:
                return SkillResult(
                    skill_id=self.skill_id,
                    output=None,
                    success=False,
                    error="房源列表不能为空",
                )

            # 生成所有组合
            tasks = []
            for prop in properties:
                for platform in platforms:
                    for ctype in content_types:
                        tasks.append({
                            "property": prop,
                            "platform": platform,
                            "content_type": ctype,
                        })

            total = len(tasks)
            results = []
            completed = 0
            failed = 0

            for i, task in enumerate(tasks):
                try:
                    result = await self._generate_single(
                        task["property"],
                        task["platform"],
                        task["content_type"],
                    )
                    results.append(result)
                    completed += 1
                except Exception as e:
                    results.append({
                        "property": task["property"].get("title", "unknown"),
                        "platform": task["platform"],
                        "content_type": task["content_type"],
                        "success": False,
                        "error": str(e),
                    })
                    failed += 1

                # 进度回调
                if progress_cb:
                    progress_cb(completed + failed, total, task)

            # 汇总
            summary = self._generate_summary(results, total, completed, failed)

            return SkillResult(
                skill_id=self.skill_id,
                output={
                    "batch_id": f"batch_{id(self)}",
                    "results": results,
                    "summary": summary,
                },
                success=True,
            )

        except Exception as e:
            logger.error(f"SK-10 execution failed: {e}")
            return SkillResult(
                skill_id=self.skill_id,
                output=None,
                success=False,
                error=str(e),
            )

    async def _generate_single(self, prop: Dict, platform: str, content_type: str) -> Dict:
        """生成单条内容"""
        title = prop.get("title", "未知房源")
        
        # 模拟异步生成（实际接入 LLM）
        await asyncio.sleep(0.1)

        return {
            "property": title,
            "platform": platform,
            "content_type": content_type,
            "success": True,
            "title": f"🏠 {title} {'探房笔记' if content_type == 'note' else '探房视频'}",
            "content": f"今天带大家来看{title}，{prop.get('highlight', '性价比超高')}！",
            "tags": ["#买房", f"#{title}", "#房产"],
        }

    def _generate_summary(self, results: List, total: int, completed: int, failed: int) -> Dict:
        """生成汇总报告"""
        platform_stats = {}
        type_stats = {}
        
        for r in results:
            plat = r.get("platform", "unknown")
            ctype = r.get("content_type", "unknown")
            platform_stats[plat] = platform_stats.get(plat, 0) + 1
            type_stats[ctype] = type_stats.get(ctype, 0) + 1

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "success_rate": f"{completed / total * 100:.1f}%" if total > 0 else "0%",
            "by_platform": platform_stats,
            "by_type": type_stats,
        }
