from django.db import models
from django.utils import timezone
from apps.users.models import User


class DifyConfig(models.Model):
    """Dify API配置"""
    api_url = models.URLField(max_length=500, verbose_name='API URL', help_text='Dify API endpoint URL')
    api_key = models.CharField(max_length=500, verbose_name='API Key', help_text='Dify API密钥')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dify_configs'
        verbose_name = 'Dify配置'
        verbose_name_plural = 'Dify配置'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dify Config - {'Active' if self.is_active else 'Inactive'}"
    
    @classmethod
    def get_active_config(cls):
        """获取当前激活的配置"""
        return cls.objects.filter(is_active=True).first()


class AssistantSession(models.Model):
    """智能助手会话记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assistant_sessions', verbose_name='用户')
    session_id = models.CharField(max_length=200, verbose_name='会话ID')
    conversation_id = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dify对话ID')
    title = models.CharField(max_length=500, blank=True, verbose_name='会话标题')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'assistant_sessions'
        verbose_name = '智能助手会话'
        verbose_name_plural = '智能助手会话'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title or self.session_id}"


class ChatMessage(models.Model):
    """聊天消息记录"""
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助手'),
    ]
    
    session = models.ForeignKey(AssistantSession, on_delete=models.CASCADE, related_name='chat_messages', verbose_name='会话')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='角色')
    content = models.TextField(verbose_name='消息内容')
    conversation_id = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dify对话ID')
    message_id = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dify消息ID')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}"


class AssistantMessage(models.Model):
    """智能助手消息记录（保留用于向后兼容）"""
    MESSAGE_TYPE_CHOICES = [
        ('user', '用户消息'),
        ('assistant', '助手回复'),
    ]
    
    session = models.ForeignKey(AssistantSession, on_delete=models.CASCADE, related_name='messages', verbose_name='会话')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    
    class Meta:
        db_table = 'assistant_messages'
        verbose_name = '智能助手消息'
        verbose_name_plural = '智能助手消息'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}"


class KnowledgeBaseDocument(models.Model):
    """知识库文档"""
    STATUS_CHOICES = [
        ('pending', '待索引'),
        ('indexing', '索引中'),
        ('indexed', '已索引'),
        ('failed', '索引失败'),
    ]
    
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('md', 'Markdown'),
        ('txt', 'Text'),
        ('doc', 'Word'),
        ('docx', 'Word'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kb_documents', verbose_name='用户')
    name = models.CharField(max_length=500, verbose_name='文档名称')
    file = models.FileField(upload_to='knowledge_base/%Y/%m/', verbose_name='文档文件')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, verbose_name='文件类型')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='索引状态')
    vector_collection_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='向量索引ID')
    index_data = models.JSONField(blank=True, null=True, verbose_name='索引数据')
    index_error = models.TextField(blank=True, verbose_name='索引错误信息')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'knowledge_base_documents'
        verbose_name = '知识库文档'
        verbose_name_plural = '知识库文档'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class KnowledgeBaseChat(models.Model):
    """知识库对话记录"""
    document = models.ForeignKey(KnowledgeBaseDocument, on_delete=models.CASCADE, related_name='chats', verbose_name='文档')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kb_chats', verbose_name='用户')
    question = models.TextField(verbose_name='问题')
    answer = models.TextField(verbose_name='回答')
    retrieved_pages = models.JSONField(blank=True, null=True, verbose_name='检索到的页面')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    
    class Meta:
        db_table = 'knowledge_base_chats'
        verbose_name = '知识库对话'
        verbose_name_plural = '知识库对话'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.question[:50]}"
