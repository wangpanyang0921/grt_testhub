from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
import requests
import os
import threading
from django.conf import settings
from .models import AssistantSession, AssistantMessage, ChatMessage, DifyConfig, KnowledgeBaseDocument, KnowledgeBaseChat
from .serializers import (
    AssistantSessionSerializer,
    AssistantSessionCreateSerializer,
    AssistantMessageSerializer,
    ChatMessageSerializer,
    KnowledgeBaseDocumentSerializer,
    KnowledgeBaseDocumentDetailSerializer,
    KnowledgeBaseChatSerializer,
    KnowledgeBaseChatCreateSerializer
)
from .rag_service import rag_service


def assistant_view(request):
    """AI助手页面视图"""
    return render(request, 'assistant/assistant.html')


class AssistantSessionViewSet(viewsets.ModelViewSet):
    """智能助手会话视图集"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AssistantSessionCreateSerializer
        return AssistantSessionSerializer
    
    def get_queryset(self):
        return AssistantSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """添加消息到会话"""
        session = self.get_object()
        serializer = AssistantMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话的聊天消息"""
        session = self.get_object()
        messages = session.chat_messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatViewSet(viewsets.ViewSet):
    """聊天功能ViewSet"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """发送消息到Dify API"""
        session_id = request.data.get('session_id')
        message = request.data.get('message')
        
        if not session_id or not message:
            return Response(
                {'error': 'session_id和message都是必填项'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取会话
        try:
            session = AssistantSession.objects.get(
                session_id=session_id,
                user=request.user
            )
        except AssistantSession.DoesNotExist:
            return Response(
                {'error': '会话不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取Dify配置
        dify_config = DifyConfig.get_active_config()
        if not dify_config:
            return Response(
                {'error': '未配置Dify API，请先在配置中心配置'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 保存用户消息
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message,
            conversation_id=session.conversation_id
        )
        
        try:
            # 准备请求数据
            payload = {
                'inputs': {},
                'query': message,
                'response_mode': 'blocking',
                'conversation_id': session.conversation_id or '',
                'user': str(request.user.id),
                'files': []
            }
            
            # 发送请求到Dify API
            response = requests.post(
                f"{dify_config.api_url}/chat-messages",
                headers={
                    'Authorization': f'Bearer {dify_config.api_key}',
                    'Content-Type': 'application/json'
                },
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 更新会话的conversation_id
                if not session.conversation_id and data.get('conversation_id'):
                    session.conversation_id = data['conversation_id']
                    session.save()
                
                # 保存助手回复
                assistant_message = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=data.get('answer', ''),
                    conversation_id=session.conversation_id,
                    message_id=data.get('message_id', '')
                )
                
                return Response({
                    'answer': data.get('answer', ''),
                    'message_id': data.get('message_id', ''),
                    'conversation_id': session.conversation_id
                })
            else:
                error_msg = f'Dify API错误: {response.status_code}'
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    pass
                
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except requests.exceptions.Timeout:
            return Response(
                {'error': '请求超时，请稍后重试'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {'error': f'网络错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class KnowledgeBaseDocumentViewSet(viewsets.ModelViewSet):
    """知识库文档视图集"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = KnowledgeBaseDocumentSerializer

    def get_queryset(self):
        return KnowledgeBaseDocument.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """重写 create 方法以正确处理文件上传"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取上传的文件
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'error': '请上传文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取文件信息
        file_name = file_obj.name
        file_size = file_obj.size
        file_type = file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        # 保存文档
        document = serializer.save(
            user=request.user,
            status='pending',
            file_size=file_size,
            file_type=file_type,
            file=file_obj
        )
        
        # 异步生成索引
        self._generate_index_async(document, request.user)
        
        return Response(
            self.get_serializer(document).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """重写 destroy 方法以同时删除向量索引"""
        document = self.get_object()
        document_id = document.id
        
        # 删除向量索引
        try:
            rag_service.delete_index(document_id)
        except Exception as e:
            # 记录错误但不阻止删除操作
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"删除文档 {document_id} 的向量索引时出错: {str(e)}")
        
        # 删除文档记录（会级联删除关联的对话记录）
        return super().destroy(request, *args, **kwargs)

    def _generate_index_async(self, document, user=None):
        """异步生成文档索引"""
        def generate():
            try:
                # 更新状态为索引中
                document.status = 'indexing'
                document.save()

                # 获取文件路径
                file_path = document.file.path

                # 检查文件是否存在
                if not os.path.exists(file_path):
                    document.status = 'failed'
                    document.index_error = '文件不存在'
                    document.save()
                    return

                # 生成索引
                result = rag_service.generate_index(
                    file_path,
                    document.file_type,
                    user=user,
                    document_id=document.id
                )

                if result['success']:
                    document.vector_collection_id = result.get('index_id')
                    document.index_data = result.get('index_data')
                    document.status = 'indexed'
                else:
                    document.status = 'failed'
                    document.index_error = result.get('error', '未知错误')

                document.save()

            except Exception as e:
                document.status = 'failed'
                document.index_error = str(e)
                document.save()

        thread = threading.Thread(target=generate)
        thread.start()

    @action(detail=True, methods=['post'])
    def reindex(self, request, pk=None):
        """重新生成索引"""
        document = self.get_object()
        # 重置状态为待索引
        document.status = 'pending'
        document.index_error = ''
        document.save()
        # 异步生成索引
        self._generate_index_async(document, request.user)
        return Response({'message': '索引生成中'}, status=status.HTTP_202_ACCEPTED)


class KnowledgeBaseChatViewSet(viewsets.ModelViewSet):
    """知识库对话视图集"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create']:
            return KnowledgeBaseChatCreateSerializer
        return KnowledgeBaseChatSerializer

    def get_queryset(self):
        return KnowledgeBaseChat.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """重写 create 方法以捕获异常"""
        try:
            return super().create(request, *args, **kwargs)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(f"问答异常: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'服务器错误: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        # 获取文档
        document_id = self.request.data.get('document')
        try:
            document = KnowledgeBaseDocument.objects.get(
                id=document_id,
                user=self.request.user
            )
        except KnowledgeBaseDocument.DoesNotExist:
            raise ValueError('文档不存在')

        # 检查文档是否已索引
        if document.status != 'indexed':
            raise ValueError('文档尚未完成索引')

        # 获取问题
        question = self.request.data.get('question', '')
        if not question:
            raise ValueError('问题不能为空')

        # 调用 RAG 服务获取答案
        index_data = {
            'index_id': document.vector_collection_id,
            'tree_structure': document.index_data
        }

        # 获取检索结果
        retrieved_docs = rag_service.retrieve_documents(
            question,
            index_data,
            user=self.request.user,
            document=document
        )

        # 生成答案
        answer = rag_service.query(question, index_data, user=self.request.user, document=document)

        # 保存对话记录
        serializer.save(
            user=self.request.user,
            document=document,
            answer=answer,
            retrieved_pages=retrieved_docs
        )

    @action(detail=False, methods=['post'], url_path='stream-chat')
    def stream_chat(self, request):
        """流式问答接口"""
        from django.http import StreamingHttpResponse
        import json

        document_id = request.data.get('document')
        question = request.data.get('question', '')

        if not document_id or not question:
            return Response(
                {'error': '文档ID和问题是必填项'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document = KnowledgeBaseDocument.objects.get(
                id=document_id,
                user=request.user
            )
        except KnowledgeBaseDocument.DoesNotExist:
            return Response({'error': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)

        if document.status != 'indexed':
            return Response({'error': '文档尚未完成索引'}, status=status.HTTP_400_BAD_REQUEST)

        def event_stream():
            """生成 SSE 流"""
            try:
                # 发送初始事件
                yield f"data: {json.dumps({'type': 'start'})}\n\n"

                # 发送思考过程
                yield f"data: {json.dumps({'type': 'thinking', 'content': '正在检索相关文档内容...'})}\n\n"

                # 调用 RAG 服务获取检索结果
                index_data = {
                    'index_id': document.vector_collection_id,
                    'tree_structure': document.index_data
                }

                # 先获取相关文档片段
                retrieved_docs = rag_service.retrieve_documents(question, index_data, user=request.user, document=document)

                if retrieved_docs:
                    yield f"data: {json.dumps({'type': 'thinking', 'content': f'找到 {len(retrieved_docs)} 个相关片段，正在分析...'})}\n\n"

                # 发送生成中标记
                yield f"data: {json.dumps({'type': 'thinking', 'content': '正在生成回答...'})}\n\n"

                # 流式生成回答
                answer_chunks = []
                for chunk in rag_service.stream_query(question, index_data, user=request.user, document=document):
                    if chunk:
                        answer_chunks.append(chunk)
                        data = json.dumps({'type': 'chunk', 'content': chunk})
                        yield f"data: {data}\n\n"

                # 合并完整回答
                full_answer = ''.join(answer_chunks)

                # 保存对话记录
                KnowledgeBaseChat.objects.create(
                    user=request.user,
                    document=document,
                    question=question,
                    answer=full_answer,
                    retrieved_pages=retrieved_docs
                )

                # 发送结束标记
                yield f"data: {json.dumps({'type': 'end', 'answer': full_answer})}\n\n"

            except Exception as e:
                import traceback
                print(f"流式问答异常: {str(e)}")
                print(traceback.format_exc())
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
