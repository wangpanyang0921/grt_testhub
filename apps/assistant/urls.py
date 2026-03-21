from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssistantSessionViewSet, ChatViewSet, assistant_view, KnowledgeBaseDocumentViewSet, KnowledgeBaseChatViewSet
from .views_config import DifyConfigViewSet

router = DefaultRouter()
router.register(r'sessions', AssistantSessionViewSet, basename='assistant-sessions')
router.register(r'chat', ChatViewSet, basename='chat')
router.register(r'config/dify', DifyConfigViewSet, basename='dify-config')
router.register(r'knowledge-base/documents', KnowledgeBaseDocumentViewSet, basename='knowledge-base-documents')
router.register(r'knowledge-base/chat', KnowledgeBaseChatViewSet, basename='knowledge-base-chat')

urlpatterns = [
    path('', include(router.urls)),
    path('view/', assistant_view, name='assistant-view'),
]