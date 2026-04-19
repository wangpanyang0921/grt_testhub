from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DataFactoryRecord(models.Model):
    """数据工厂使用记录"""

    TOOL_CATEGORIES = (
        ('test_data', '测试数据'),
        ('json', 'JSON工具'),
        ('string', '字符工具'),
        ('encoding', '编码工具'),
        ('random', '随机工具'),
        ('encryption', '加密工具'),
        ('crontab', 'Crontab工具'),
    )

    TOOL_SCENARIOS = (
        ('test_data', '测试数据'),
        ('json', 'JSON工具'),
        ('string', '字符工具'),
        ('encoding', '编码工具'),
        ('random', '随机工具'),
        ('encryption', '加密工具'),
        ('crontab', 'Crontab工具'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    tool_name = models.CharField(max_length=100, verbose_name='工具名称')
    tool_category = models.CharField(max_length=20, choices=TOOL_CATEGORIES, verbose_name='工具分类')
    tool_scenario = models.CharField(max_length=20, choices=TOOL_SCENARIOS, verbose_name='使用场景')
    custom_name = models.CharField(max_length=200, verbose_name='自定义名称', null=True, blank=True)
    input_data = models.JSONField(verbose_name='输入数据', null=True, blank=True)
    output_data = models.JSONField(verbose_name='输出数据')
    is_saved = models.BooleanField(default=True, verbose_name='是否保存')
    tags = models.JSONField(verbose_name='标签', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'data_factory_record'
        verbose_name = '数据工厂记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['tool_category']),
            models.Index(fields=['tool_scenario']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.tool_name}"


class BugAnalysisRecord(models.Model):
    """
    Bug 分析记录

    支持历史回溯和跨版本趋势对比:
    - 保存原始 Bug 数据 + 完整分析结果
    - 支持版本标签标记 (如 "v6.0.0-2026-04-16")
    - 记录数据来源 (Excel上传 / API同步)
    - AI 增强分析结果也保存在此
    """

    SOURCE_TYPE_CHOICES = (
        ('excel', 'Excel上传'),
        ('json_api', 'JSON API'),
        ('yunxiao_api', '云效API'),
        ('tapd_api', 'TAPD API'),
    )

    id = models.AutoField(primary_key=True)
    version_tag = models.CharField(max_length=100, verbose_name='版本标签', default='', blank=True,
                                     help_text="如 v6.0.0-release、2026-Q2-sprint5 等")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default='excel',
                                    verbose_name='数据来源')
    file_name = models.CharField(max_length=255, blank=True, default='', verbose_name='源文件名')
    total_bugs = models.IntegerField(default=0, verbose_name='Bug总数')

    # 原始数据: 标准化后的 Bug 列表 (每条包含 title/desc/severity/status/creator/created/module/defect_type/inferred_sev 等)
    raw_bugs = models.JSONField(default=list, verbose_name='原始Bug数据')

    # 分析结果: analyze_bugs() 返回的完整字典 (含 modulesData/severityCrossData/riskData 等全部维度)
    analysis_result = models.JSONField(default=dict, verbose_name='分析结果')

    # 元信息
    created_by = models.CharField(max_length=50, default='system', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'df_bug_analysis_record'
        verbose_name = 'Bug分析记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['source_type']),
            models.Index(fields=['version_tag']),
            models.Index(fields=['total_bugs']),
        ]

    def __str__(self):
        tag = f"[{self.version_tag}]" if self.version_tag else ""
        return f"Bug分析 {tag} {self.file_name or self.source_type} ({self.total_bugs}条) @{self.created_at:%Y-%m-%d %H:%M}"

    @property
    def p0_count(self) -> int:
        """推断 P0 数量"""
        return (self.analysis_result or {}).get('sevInfData', {}).get('推断P0', 0)

    @property
    def p1_count(self) -> int:
        """推断 P1 数量"""
        return (self.analysis_result or {}).get('sevInfData', {}).get('推断P1', 0)

    @property
    def top_module(self) -> str:
        """Bug数最多的模块"""
        modules = (self.analysis_result or {}).get('modulesData', {})
        if modules:
            return max(modules.items(), key=lambda x: x[1])[0]
        return ''
