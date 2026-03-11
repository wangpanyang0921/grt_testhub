"""
AI 缓存使用示例
展示如何在 AI 执行引擎中使用缓存机制
"""

# ============================================================
# 示例 1: 基础缓存使用
# ============================================================

from apps.ui_automation.ai_cache import (
    ai_cache,           # 全局缓存管理器
    TaskAnalysisCache,  # 任务分析缓存
    ActionPlanCache,    # 操作计划缓存
    ExecutionHistoryCache,  # 执行历史缓存
    cached_task_analysis,   # 装饰器
)


def example_basic_usage():
    """基础缓存使用示例"""
    
    # 1. 直接设置和获取缓存
    ai_cache.set("my_key", {"data": "value"}, ttl_seconds=3600)
    result = ai_cache.get("my_key")
    print(f"缓存结果: {result}")
    
    # 2. 任务分析缓存
    task = "打开百度，搜索'测试平台'"
    planned_tasks = [
        {"id": 1, "description": "打开百度首页", "status": "pending"},
        {"id": 2, "description": "在搜索框输入'测试平台'", "status": "pending"},
        {"id": 3, "description": "点击搜索按钮", "status": "pending"},
    ]
    
    # 缓存任务分析结果
    TaskAnalysisCache.set(task, planned_tasks, ttl_hours=24)
    
    # 获取缓存的任务分析结果
    cached_tasks = TaskAnalysisCache.get(task)
    if cached_tasks:
        print(f"命中缓存: {cached_tasks}")
    else:
        print("缓存未命中")


# ============================================================
# 示例 2: 在 AI 执行中使用缓存
# ============================================================

class AICacheExample:
    """AI 缓存使用示例类"""
    
    async def analyze_task_with_cache(self, task_description: str):
        """
        带缓存的任务分析
        实际代码已集成到 ai_base.py 中
        """
        from apps.ui_automation.ai_cache import TaskAnalysisCache
        
        # 1. 先查缓存
        cached = TaskAnalysisCache.get(task_description)
        if cached:
            print(f"[Cache Hit] 使用缓存的任务分析结果")
            return cached
        
        # 2. 缓存未命中，调用 LLM
        print(f"[Cache Miss] 调用 LLM 分析任务...")
        # ... 调用 LLM 的代码 ...
        result = [
            {"id": 1, "description": "步骤1", "status": "pending"},
            {"id": 2, "description": "步骤2", "status": "pending"},
        ]
        
        # 3. 存入缓存
        TaskAnalysisCache.set(task_description, result, ttl_hours=24)
        
        return result
    
    async def execute_step_with_cache(self, step: str, page_state: dict):
        """
        带缓存的步骤执行
        """
        from apps.ui_automation.ai_cache import ActionPlanCache
        
        page_url = page_state.get('url')
        page_hash = self._compute_page_hash(page_state)
        
        # 1. 查缓存
        cached_actions = ActionPlanCache.get(step, page_url, page_hash)
        if cached_actions:
            print(f"[Cache Hit] 使用缓存的操作计划")
            return cached_actions
        
        # 2. 缓存未命中，调用 LLM 生成操作
        print(f"[Cache Miss] 生成操作计划...")
        actions = {"action": "click", "target": "#search-btn"}
        
        # 3. 存入缓存
        ActionPlanCache.set(step, page_url, page_hash, actions, ttl_hours=1)
        
        return actions
    
    def _compute_page_hash(self, page_state: dict) -> str:
        """计算页面状态哈希，用于缓存键"""
        import hashlib
        content = page_state.get('html', '')[:1000]  # 取前1000字符
        return hashlib.md5(content.encode()).hexdigest()[:8]


# ============================================================
# 示例 3: 使用装饰器自动缓存
# ============================================================

from apps.ui_automation.ai_cache import cached_task_analysis


class MyAIAgent:
    """使用装饰器的 AI Agent 示例"""
    
    @cached_task_analysis(ttl_hours=24)
    async def analyze_task(self, task_description: str):
        """
        自动缓存的任务分析方法
        只需要添加装饰器，无需手动处理缓存逻辑
        """
        # 这里是实际的分析逻辑
        # 装饰器会自动处理缓存的读取和写入
        
        # 模拟 LLM 调用
        await asyncio.sleep(1)
        
        return [
            {"id": 1, "description": f"分析: {task_description[:20]}...", "status": "pending"}
        ]


# ============================================================
# 示例 4: 缓存预热策略
# ============================================================

async def warmup_cache():
    """
    缓存预热 - 在系统启动时预热常用任务
    """
    from apps.ui_automation.ai_base import BaseBrowserAgent
    
    agent = BaseBrowserAgent()
    
    # 常用任务列表
    common_tasks = [
        "打开百度，搜索'测试平台'",
        "访问登录页面，输入用户名admin，密码123456",
        "打开项目列表，点击新建项目按钮",
        "进入用户管理，搜索用户并编辑",
    ]
    
    print("开始预热缓存...")
    for task in common_tasks:
        # 调用分析任务，结果会自动缓存
        await agent.analyze_task(task)
        print(f"预热完成: {task[:30]}...")
    
    print("缓存预热完成！")


# ============================================================
# 示例 5: 缓存失效策略
# ============================================================

def invalidate_cache_examples():
    """缓存失效示例"""
    from apps.ui_automation.ai_cache import ai_cache
    
    # 1. 删除特定缓存
    ai_cache.delete("task_analysis:abc123")
    
    # 2. 清空所有缓存
    ai_cache.clear_all()
    
    # 3. 使用通配符删除（需要配合 Redis）
    # 删除所有任务分析缓存
    # redis_client.delete_pattern("task_analysis:*")


# ============================================================
# 示例 6: 性能对比测试
# ============================================================

import time
import asyncio


async def performance_comparison():
    """
    性能对比测试：缓存 vs 无缓存
    """
    from apps.ui_automation.ai_base import BaseBrowserAgent
    
    agent = BaseBrowserAgent()
    task = "打开百度，搜索'测试平台'，点击第一个结果"
    
    # 测试 1: 无缓存（第一次）
    print("=== 测试 1: 无缓存（第一次执行）===")
    start = time.time()
    result1 = await agent.analyze_task(task)
    duration1 = time.time() - start
    print(f"耗时: {duration1:.2f}秒")
    
    # 测试 2: 有缓存（第二次）
    print("\n=== 测试 2: 有缓存（第二次执行）===")
    start = time.time()
    result2 = await agent.analyze_task(task)
    duration2 = time.time() - start
    print(f"耗时: {duration2:.2f}秒")
    
    # 性能提升
    if duration2 > 0:
        speedup = duration1 / duration2
        print(f"\n性能提升: {speedup:.1f}x")
        print(f"节省时间: {duration1 - duration2:.2f}秒")


# ============================================================
# 示例 7: 在 Django View 中使用
# ============================================================

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def get_cache_stats(request):
    """获取缓存统计信息 API"""
    from apps.ui_automation.ai_cache import CacheStats, ai_cache
    import os
    
    stats = CacheStats.get_stats()
    cache_files = os.listdir(ai_cache.cache_dir)
    
    return Response({
        "cache_stats": stats,
        "memory_entries": len(ai_cache._memory_cache),
        "file_entries": len([f for f in cache_files if f.endswith('.pkl')]),
    })


@api_view(['POST'])
def clear_ai_cache(request):
    """清空 AI 缓存 API"""
    from apps.ui_automation.ai_cache import ai_cache, CacheStats
    
    ai_cache.clear_all()
    CacheStats.reset()
    
    return Response({"message": "AI 缓存已清空"})


# ============================================================
# 运行示例
# ============================================================

if __name__ == "__main__":
    # 运行基础示例
    example_basic_usage()
    
    # 运行性能对比
    # asyncio.run(performance_comparison())
