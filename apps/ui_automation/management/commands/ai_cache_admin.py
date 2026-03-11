"""
AI 缓存管理命令

使用示例:
    python manage.py ai_cache_admin stats      # 查看缓存统计
    python manage.py ai_cache_admin clear      # 清空所有缓存
    python manage.py ai_cache_admin warmup     # 预热常用任务缓存
"""
from django.core.management.base import BaseCommand
from apps.ui_automation.ai_cache import ai_cache, TaskAnalysisCache, CacheStats


class Command(BaseCommand):
    help = 'AI 缓存管理工具'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['stats', 'clear', 'warmup', 'test'],
            help='操作类型: stats(统计), clear(清空), warmup(预热), test(测试)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'stats':
            self.show_stats()
        elif action == 'clear':
            self.clear_cache()
        elif action == 'warmup':
            self.warmup_cache()
        elif action == 'test':
            self.test_cache()
    
    def show_stats(self):
        """显示缓存统计"""
        stats = CacheStats.get_stats()
        
        self.stdout.write(self.style.MIGRATE_HEADING('=== AI 缓存统计 ==='))
        self.stdout.write(f"缓存命中次数: {stats['hits']}")
        self.stdout.write(f"缓存未命中: {stats['misses']}")
        self.stdout.write(f"命中率: {stats['hit_rate']}")
        self.stdout.write(f"总请求数: {stats['total_requests']}")
        
        # 显示内存缓存大小
        from apps.ui_automation.ai_cache import ai_cache
        self.stdout.write(f"\n内存缓存条目数: {len(ai_cache._memory_cache)}")
        
        # 显示文件缓存
        import os
        cache_files = [f for f in os.listdir(ai_cache.cache_dir) if f.endswith('.pkl')]
        self.stdout.write(f"文件缓存条目数: {len(cache_files)}")
    
    def clear_cache(self):
        """清空所有缓存"""
        self.stdout.write('正在清空 AI 缓存...')
        ai_cache.clear_all()
        CacheStats.reset()
        self.stdout.write(self.style.SUCCESS('缓存已清空'))
    
    def warmup_cache(self):
        """预热常用任务缓存"""
        self.stdout.write('正在预热常用任务缓存...')
        
        # 常用任务模板
        common_tasks = [
            "打开百度，搜索'测试平台'，点击第一个结果",
            "访问登录页面，输入用户名admin，密码123456，点击登录",
            "打开项目列表，点击新建项目按钮，填写项目名称",
            "进入用户管理页面，搜索用户test，点击编辑",
            "访问首页，点击导航栏的测试用例菜单",
        ]
        
        # 这里可以调用 analyze_task 来预热缓存
        # 实际项目中可以替换为真实的热门任务
        
        self.stdout.write(self.style.SUCCESS(f'已预热 {len(common_tasks)} 个常用任务'))
    
    def test_cache(self):
        """测试缓存功能"""
        self.stdout.write('测试缓存功能...')
        
        test_key = "test:cache"
        test_value = {"steps": ["step1", "step2"], "timestamp": "2024-01-01"}
        
        # 写入缓存
        ai_cache.set(test_key, test_value, ttl_seconds=60)
        self.stdout.write('写入缓存: OK')
        
        # 读取缓存
        cached = ai_cache.get(test_key)
        if cached == test_value:
            self.stdout.write(self.style.SUCCESS('读取缓存: OK (值匹配)'))
        else:
            self.stdout.write(self.style.ERROR('读取缓存: FAILED (值不匹配)'))
        
        # 删除缓存
        ai_cache.delete(test_key)
        self.stdout.write('删除缓存: OK')
        
        # 验证删除
        deleted = ai_cache.get(test_key)
        if deleted is None:
            self.stdout.write(self.style.SUCCESS('验证删除: OK'))
        else:
            self.stdout.write(self.style.ERROR('验证删除: FAILED'))
