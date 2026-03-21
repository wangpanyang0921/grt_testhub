from rest_framework import serializers
from .models import AssistantSession, AssistantMessage, DifyConfig, ChatMessage, KnowledgeBaseDocument, KnowledgeBaseChat


class DifyConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifyConfig
        fields = ['id', 'api_url', 'api_key', 'is_active', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True}  # Don't expose API key in responses
        }


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'conversation_id', 'message_id', 'created_at']
        read_only_fields = ['conversation_id', 'message_id', 'created_at']


class AssistantMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantMessage
        fields = ['id', 'message_type', 'content', 'created_at']


class AssistantSessionSerializer(serializers.ModelSerializer):
    messages = AssistantMessageSerializer(many=True, read_only=True)
    chat_messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = AssistantSession
        fields = ['id', 'session_id', 'conversation_id', 'title', 'created_at', 'updated_at', 'messages', 'chat_messages']


class AssistantSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantSession
        fields = ['session_id', 'title']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserSerializer(serializers.Serializer):
    """用户信息序列化器"""
    id = serializers.IntegerField()
    username = serializers.CharField()


class KnowledgeBaseDocumentSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBaseDocument
        fields = ['id', 'name', 'file_type', 'file_size', 'status', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['file_type', 'file_size', 'status', 'created_by', 'created_at', 'updated_at']
    
    def get_created_by(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username
            }
        return None


class KnowledgeBaseDocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseDocument
        fields = ['id', 'name', 'file', 'file_type', 'file_size', 'status', 'index_data', 'index_error', 'created_at', 'updated_at']
        read_only_fields = ['file_type', 'file_size', 'status', 'index_data', 'index_error', 'created_at', 'updated_at']


class KnowledgeBaseChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseChat
        fields = ['id', 'question', 'answer', 'retrieved_pages', 'created_at']
        read_only_fields = ['answer', 'retrieved_pages', 'created_at']


class KnowledgeBaseChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseChat
        fields = ['id', 'document', 'question', 'answer', 'retrieved_pages', 'created_at']
        read_only_fields = ['answer', 'retrieved_pages', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
