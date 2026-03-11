"""
AI 用例执行缓存模块
提供多级缓存机制，加速 AI 测试执行
"""
import hashlib
import json
import pickle
import logging
from typing import Optional, Any, List, Dict
from functools import wraps
from datetime import datetime, timedelta
import os

logger = logging.getLogger('django')


class AICacheManager:
    """
    AI 执行缓存管理器
    支持三级缓存：内存 -> Redis -> 本地文件
    """
    
    def __init__(self):
        self._memory_cache = {}  # L1: 内存缓存
        self._memory_ttl = {}    # 内存缓存过期时间
        self.redis_enabled = self._check_redis()
        self.cache_dir = self._get_cache_dir()
        
    def _check_redis(self) -> bool:
        """检查是否可用 Redis"""
        try:
            from django.core.cache import cache
            cache.set('test_key', 'test_value', 1)
            return cache.get('test_key') == 'test_value'
        except:
            return False
    
    def _get_cache_dir(self) -> str:
        """获取本地缓存目录"""
        from django.conf import settings
        cache_dir = os.path.join(settings.BASE_DIR, 'temp', 'ai_cache')
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """生成缓存键"""
        if isinstance(data, str):
            key_data = data
        else:
            key_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
        
        hash_value = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_value}"
    
    def _get_from_memory(self, key: str) -> Optional[Any]:
        """从内存缓存获取"""
        if key in self._memory_cache:
            if datetime.now() < self._memory_ttl.get(key, datetime.min):
                logger.debug(f"[Cache] Memory hit: {key}")
                return self._memory_cache[key]
            else:
                # 过期清理
                del self._memory_cache[key]
                del self._memory_ttl[key]
        return None
    
    def _set_to_memory(self, key: str, value: Any, ttl_seconds: int = 300):
        """设置内存缓存"""
        self._memory_cache[key] = value
        self._memory_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
        
        # 内存缓存大小限制（防止OOM）
        if len(self._memory_cache) > 1000:
            self._cleanup_memory_cache()
    
    def _cleanup_memory_cache(self):
        """清理过期的内存缓存"""
        now = datetime.now()
        expired_keys = [
            k for k, v in self._memory_ttl.items() 
            if now > v
        ]
        for k in expired_keys:
            del self._memory_cache[k]
            del self._memory_ttl[k]
        logger.info(f"[Cache] Cleaned up {len(expired_keys)} expired memory cache entries")
    
    def _get_from_redis(self, key: str) -> Optional[Any]:
        """从 Redis 获取"""
        if not self.redis_enabled:
            return None
        try:
            from django.core.cache import cache
            value = cache.get(key)
            if value:
                logger.debug(f"[Cache] Redis hit: {key}")
                return pickle.loads(value)
        except Exception as e:
            logger.warning(f"[Cache] Redis get failed: {e}")
        return None
    
    def _set_to_redis(self, key: str, value: Any, ttl_seconds: int = 3600):
        """设置 Redis 缓存"""
        if not self.redis_enabled:
            return
        try:
            from django.core.cache import cache
            cache.set(key, pickle.dumps(value), ttl_seconds)
        except Exception as e:
            logger.warning(f"[Cache] Redis set failed: {e}")
    
    def _get_from_file(self, key: str) -> Optional[Any]:
        """从本地文件获取"""
        file_path = os.path.join(self.cache_dir, f"{key.replace(':', '_')}.pkl")
        if os.path.exists(file_path):
            try:
                # 检查文件年龄
                stat = os.stat(file_path)
                file_age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)
                if file_age.days > 7:  # 文件超过7天过期
                    os.remove(file_path)
                    return None
                
                with open(file_path, 'rb') as f:
                    logger.debug(f"[Cache] File hit: {key}")
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"[Cache] File read failed: {e}")
        return None
    
    def _set_to_file(self, key: str, value: Any):
        """设置本地文件缓存"""
        file_path = os.path.join(self.cache_dir, f"{key.replace(':', '_')}.pkl")
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.warning(f"[Cache] File write failed: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存（按 L1 -> L2 -> L3 顺序）
        """
        # L1: 内存
        value = self._get_from_memory(key)
        if value is not None:
            return value
        
        # L2: Redis
        value = self._get_from_redis(key)
        if value is not None:
            # 回填内存缓存
            self._set_to_memory(key, value)
            return value
        
        # L3: 本地文件
        value = self._get_from_file(key)
        if value is not None:
            # 回填上层缓存
            self._set_to_memory(key, value)
            self._set_to_redis(key, value)
            return value
        
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """
        设置缓存（同时写入三级缓存）
        """
        # L1: 内存（短TTL）
        self._set_to_memory(key, value, min(ttl_seconds, 300))
        
        # L2: Redis
        self._set_to_redis(key, value, ttl_seconds)
        
        # L3: 本地文件（大对象或永久缓存）
        if ttl_seconds > 86400 or ttl_seconds == 0:  # >1天或永久
            self._set_to_file(key, value)
    
    def delete(self, key: str):
        """删除缓存"""
        # 删除内存缓存
        if key in self._memory_cache:
            del self._memory_cache[key]
            del self._memory_ttl[key]
        
        # 删除 Redis
        if self.redis_enabled:
            try:
                from django.core.cache import cache
                cache.delete(key)
            except:
                pass
        
        # 删除文件
        file_path = os.path.join(self.cache_dir, f"{key.replace(':', '_')}.pkl")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def clear_all(self):
        """清空所有缓存"""
        self._memory_cache.clear()
        self._memory_ttl.clear()
        
        if self.redis_enabled:
            try:
                from django.core.cache import cache
                cache.clear()
            except:
                pass
        
        # 清空文件缓存
        for f in os.listdir(self.cache_dir):
            if f.endswith('.pkl'):
                os.remove(os.path.join(self.cache_dir, f))


# 全局缓存管理器实例
ai_cache = AICacheManager()


class TaskAnalysisCache:
    """
    任务分析结果缓存
    缓存自然语言 -> 步骤列表 的映射
    """
    
    @staticmethod
    def get_cache_key(task_description: str) -> str:
        """生成任务分析缓存键"""
        return ai_cache._generate_key("task_analysis", task_description)
    
    @classmethod
    def get(cls, task_description: str) -> Optional[List[Dict]]:
        """获取缓存的任务分析结果"""
        key = cls.get_cache_key(task_description)
        result = ai_cache.get(key)
        if result:
            logger.info(f"[TaskAnalysisCache] Cache hit for task: {task_description[:50]}...")
        return result
    
    @classmethod
    def set(cls, task_description: str, planned_tasks: List[Dict], ttl_hours: int = 24):
        """缓存任务分析结果"""
        key = cls.get_cache_key(task_description)
        ai_cache.set(key, planned_tasks, ttl_hours * 3600)
        logger.info(f"[TaskAnalysisCache] Cached task analysis: {task_description[:50]}...")


class ActionPlanCache:
    """
    操作计划缓存
    缓存 步骤+页面状态 -> 操作指令 的映射
    """
    
    @staticmethod
    def get_cache_key(task_step: str, page_url: str, page_hash: str = "") -> str:
        """生成操作计划缓存键"""
        data = {
            "step": task_step,
            "url": page_url,
            "hash": page_hash  # 页面内容哈希，用于验证页面是否变化
        }
        return ai_cache._generate_key("action_plan", data)
    
    @classmethod
    def get(cls, task_step: str, page_url: str, page_hash: str = "") -> Optional[Dict]:
        """获取缓存的操作计划"""
        key = cls.get_cache_key(task_step, page_url, page_hash)
        return ai_cache.get(key)
    
    @classmethod
    def set(cls, task_step: str, page_url: str, page_hash: str, 
            actions: Dict, ttl_hours: int = 1):
        """缓存操作计划"""
        key = cls.get_cache_key(task_step, page_url, page_hash)
        ai_cache.set(key, actions, ttl_hours * 3600)


class ExecutionHistoryCache:
    """
    执行历史缓存
    用于快速回放和结果复用
    """
    
    @staticmethod
    def get_cache_key(case_id: int, task_description: str) -> str:
        """生成执行历史缓存键"""
        data = {"case_id": case_id, "task": task_description}
        return ai_cache._generate_key("execution_history", data)
    
    @classmethod
    def get(cls, case_id: int, task_description: str) -> Optional[Dict]:
        """获取缓存的执行历史"""
        key = cls.get_cache_key(case_id, task_description)
        return ai_cache.get(key)
    
    @classmethod
    def set(cls, case_id: int, task_description: str, 
            execution_result: Dict, ttl_days: int = 7):
        """缓存执行历史"""
        key = cls.get_cache_key(case_id, task_description)
        ai_cache.set(key, execution_result, ttl_days * 86400)


def cached_task_analysis(ttl_hours: int = 24):
    """
    任务分析缓存装饰器
    
    使用示例:
        @cached_task_analysis(ttl_hours=24)
        async def analyze_task(self, task_description: str):
            # 分析任务逻辑
            return planned_tasks
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, task_description: str, *args, **kwargs):
            # 尝试从缓存获取
            cached_result = TaskAnalysisCache.get(task_description)
            if cached_result is not None:
                return cached_result
            
            # 执行原函数
            result = await func(self, task_description, *args, **kwargs)
            
            # 缓存结果
            if result:
                TaskAnalysisCache.set(task_description, result, ttl_hours)
            
            return result
        return wrapper
    return decorator


def cached_action_plan(ttl_hours: int = 1):
    """
    操作计划缓存装饰器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, task_step: str, page_state: Dict, *args, **kwargs):
            page_url = page_state.get('url', '')
            page_hash = page_state.get('content_hash', '')
            
            # 尝试从缓存获取
            cached_result = ActionPlanCache.get(task_step, page_url, page_hash)
            if cached_result is not None:
                return cached_result
            
            # 执行原函数
            result = await func(self, task_step, page_state, *args, **kwargs)
            
            # 缓存结果
            if result:
                ActionPlanCache.set(task_step, page_url, page_hash, result, ttl_hours)
            
            return result
        return wrapper
    return decorator


# 缓存统计和监控
class CacheStats:
    """缓存统计信息"""
    
    hits = 0
    misses = 0
    
    @classmethod
    def record_hit(cls):
        cls.hits += 1
    
    @classmethod
    def record_miss(cls):
        cls.misses += 1
    
    @classmethod
    def get_stats(cls) -> Dict:
        total = cls.hits + cls.misses
        hit_rate = (cls.hits / total * 100) if total > 0 else 0
        return {
            "hits": cls.hits,
            "misses": cls.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total
        }
    
    @classmethod
    def reset(cls):
        cls.hits = 0
        cls.misses = 0
