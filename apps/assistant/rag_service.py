"""
RAG (Retrieval-Augmented Generation) 服务
使用 LangChain + Chroma 实现文档索引和问答
"""
import os
import logging
from typing import Optional, Dict, Any, List
from django.conf import settings

logger = logging.getLogger(__name__)


class DashScopeEmbeddings:
    """通义千问 DashScope Embedding 实现"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-v3"):
        self.api_key = api_key
        self.model = model
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入多个文档"""
        import requests
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        embeddings = []
        # DashScope 支持批量，但为安全起见，逐个处理
        for text in texts:
            payload = {
                "model": self.model,
                "input": {
                    "texts": [text]
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "output" in result and "embeddings" in result["output"]:
                embedding = result["output"]["embeddings"][0]["embedding"]
                embeddings.append(embedding)
            else:
                raise ValueError(f"Embedding API 返回错误: {result}")
                
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入查询文本"""
        result = self.embed_documents([text])
        return result[0]


class RAGService:
    """RAG 服务类 - 基于 LangChain + Chroma"""

    def __init__(self):
        self.persist_directory = os.path.join(settings.BASE_DIR, 'data', 'chroma_db')
        # 确保目录存在
        os.makedirs(self.persist_directory, exist_ok=True)

    def _get_model_config(self, user=None) -> Optional[Dict[str, Any]]:
        """获取 AI 模型配置 - 优先使用 knowledge_base 角色的配置"""
        try:
            from apps.requirement_analysis.models import AIModelConfig

            # 构建查询条件
            query = {'is_active': True}
            if user:
                query['created_by'] = user

            # 优先查找 knowledge_base 角色的配置
            kb_query = query.copy()
            kb_query['role'] = 'knowledge_base'
            config = AIModelConfig.objects.filter(**kb_query).first()

            if not config:
                # 如果没有 knowledge_base 配置，使用任意一个激活的配置作为 fallback
                config = AIModelConfig.objects.filter(**query).first()
                if config:
                    logger.warning(f"未找到 knowledge_base 角色的模型配置，使用 {config.role} 角色配置 '{config.name}' 作为替代")

            if config:
                return {
                    'model_type': config.model_type,
                    'model_name': config.model_name,
                    'api_key': config.api_key,
                    'api_base': config.base_url,
                    'temperature': getattr(config, 'temperature', 0.7),
                    'top_p': getattr(config, 'top_p', 0.9)
                }
            else:
                logger.error("没有找到任何激活的 AI 模型配置")
        except Exception as e:
            logger.error(f"获取模型配置失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        return None

    def _get_prompt_template(self) -> str:
        """获取知识库问答提示词配置"""
        try:
            from apps.requirement_analysis.models import PromptConfig

            # 获取启用的知识库提示词配置
            config = PromptConfig.get_active_config('knowledge_base')
            if config and config.content:
                logger.info(f"使用配置的知识库提示词: {config.name}")
                # 确保提示词包含必要的变量
                content = config.content
                if '{context}' not in content:
                    content += "\n\n文档内容：\n{context}"
                if '{question}' not in content:
                    content += "\n\n问题：\n{question}"
                return content
        except Exception as e:
            logger.warning(f"获取知识库提示词配置失败: {str(e)}")

        # 默认提示词
        return """你是一个专业的文档问答助手。请严格基于以下文档内容回答问题。

重要要求：
1. 如果文档中有明确的数字、时间、限制等具体信息，请直接给出精确答案
2. 优先回答问题的核心要点，不要罗列无关信息
3. 如果涉及规定、限制、标准等，请给出具体的数值或明确结论
4. 如果文档中没有明确答案，请直接说明"文档中未明确说明"

文档内容：
{context}

问题：{question}

请给出精确、简洁的回答："""

    def _is_dashscope(self, model_config: Dict[str, Any]) -> bool:
        """判断是否是通义千问/DashScope"""
        model_name = model_config.get('model_name', '')
        api_base = model_config.get('api_base', '')
        return 'qwen' in model_name.lower() or 'dashscope' in api_base.lower()

    def _get_embeddings(self, model_config: Dict[str, Any]):
        """获取 Embedding 模型"""
        if self._is_dashscope(model_config):
            # 使用通义千问 DashScope Embedding
            return DashScopeEmbeddings(
                api_key=model_config.get('api_key'),
                model='text-embedding-v3'
            )
        else:
            # 使用 OpenAI Embedding
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                openai_api_key=model_config.get('api_key'),
                openai_api_base=model_config.get('api_base'),
                model='text-embedding-ada-002'
            )

    def _extract_text(self, file_path: str, file_type: str) -> str:
        """从文档中提取文本"""
        try:
            if file_type == 'pdf':
                try:
                    import PyPDF2
                    text = ""
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    logger.error("PyPDF2 未安装，尝试使用其他方式")
                    return self._read_as_text(file_path)
            elif file_type in ['doc', 'docx']:
                try:
                    import docx2txt
                    return docx2txt.process(file_path)
                except ImportError:
                    logger.error("docx2txt 未安装，尝试使用其他方式")
                    return self._read_as_text(file_path)
            else:
                return self._read_as_text(file_path)
        except Exception as e:
            logger.error(f"提取文本失败 {file_path}: {str(e)}")
            return self._read_as_text(file_path)

    def _read_as_text(self, file_path: str) -> str:
        """作为纯文本读取"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except:
                with open(file_path, 'rb') as f:
                    return f.read().decode('utf-8', errors='ignore')

    def _split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """将文本分割成块"""
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap

        return chunks

    def generate_index(self, file_path: str, file_type: str, user=None, document_id=None) -> Dict[str, Any]:
        """
        生成文档索引

        Args:
            file_path: 文档文件路径
            file_type: 文件类型
            user: 当前用户
            document_id: 文档ID，用于作为 collection 名称

        Returns:
            索引结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise ValueError(f"文件不存在: {file_path}")

            logger.info(f"开始处理文档: {file_path}")

            # 获取模型配置
            model_config = self._get_model_config(user)
            if not model_config:
                raise ValueError("未找到可用的 AI 模型配置")

            # 提取文本
            text = self._extract_text(file_path, file_type)
            if not text.strip():
                raise ValueError("无法从文档中提取文本")

            logger.info(f"文本提取成功，长度: {len(text)} 字符")

            # 文本分块
            chunks = self._split_text(text, chunk_size=1000, chunk_overlap=200)
            logger.info(f"文档分块完成，共 {len(chunks)} 块")

            # 导入必要的库
            from langchain_chroma import Chroma
            from langchain_core.documents import Document

            # 获取 embeddings
            embeddings = self._get_embeddings(model_config)

            # 创建 Document 对象列表
            documents = [
                Document(page_content=chunk, metadata={"chunk_index": i, "source": file_path})
                for i, chunk in enumerate(chunks)
            ]

            # 使用 document_id 作为 collection 名称，实现文档隔离
            collection_name = f"doc_{document_id}" if document_id else "default"

            # 创建 vector store
            # 新版本的 Chroma 使用 persist_directory 参数自动持久化
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=self.persist_directory,
                collection_name=collection_name
            )

            logger.info(f"文档索引生成成功: {file_path}, collection: {collection_name}")

            return {
                'success': True,
                'index_id': collection_name,
                'index_data': {
                    'chunks_count': len(chunks),
                    'text_length': len(text),
                    'file_path': file_path
                },
                'pages': len(chunks)
            }

        except Exception as e:
            logger.error(f"生成索引失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

    def query_document(self, question: str, index_data: Dict[str, Any], user=None, document=None) -> Dict[str, Any]:
        """
        基于索引回答问题

        Args:
            question: 用户问题
            index_data: 文档索引数据（包含 index_id）
            user: 当前用户
            document: 文档对象

        Returns:
            回答结果
        """
        try:
            # 获取索引 ID
            collection_name = index_data.get('index_id') if isinstance(index_data, dict) else None

            if not collection_name and document:
                collection_name = f"doc_{document.id}"

            if not collection_name:
                return {
                    'success': False,
                    'error': '未找到有效的索引 ID'
                }

            logger.info(f"开始查询，collection: {collection_name}, 问题: {question}")

            # 获取模型配置
            model_config = self._get_model_config(user)
            if not model_config:
                return {
                    'success': False,
                    'error': '未找到可用的 AI 模型配置'
                }

            # 导入必要的库
            from langchain_openai import ChatOpenAI
            from langchain_chroma import Chroma
            from langchain_core.prompts import PromptTemplate
            from langchain_core.runnables import RunnablePassthrough
            from langchain_core.output_parsers import StrOutputParser

            # 获取 embeddings
            embeddings = self._get_embeddings(model_config)

            # 加载 vector store
            vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name=collection_name
            )

            # 获取 LLM
            llm = ChatOpenAI(
                openai_api_key=model_config.get('api_key'),
                openai_api_base=model_config.get('api_base'),
                model_name=model_config.get('model_name', 'gpt-3.5-turbo'),
                temperature=model_config.get('temperature', 0.7),
                model_kwargs={
                    'top_p': model_config.get('top_p', 0.9)
                }
            )

            # 创建检索器 - 使用 MMR 增加多样性，提高检索质量
            retriever = vector_store.as_retriever(
                search_type="mmr",  # 最大边际相关性，平衡相关性和多样性
                search_kwargs={
                    "k": 5,  # 返回 5 个结果
                    "fetch_k": 10,  # 从 10 个候选中选择
                    "lambda_mult": 0.7  # 相关性权重（0-1，越高越注重相关性）
                }
            )

            # 获取提示词配置
            prompt_template = self._get_prompt_template()

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )

            # 使用 LCEL 构建 RAG 链
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | PROMPT
                | llm
                | StrOutputParser()
            )

            # 执行查询
            answer = rag_chain.invoke(question)

            # 获取来源文档
            source_docs = retriever.invoke(question)

            # 提取来源信息
            sources = []
            for doc in source_docs:
                sources.append({
                    'content': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content,
                    'metadata': doc.metadata
                })

            logger.info(f"查询完成，找到 {len(sources)} 个相关文本块")

            return {
                'success': True,
                'answer': answer,
                'retrieved_pages': sources
            }

        except Exception as e:
            logger.error(f"问答失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

    def delete_index(self, document_id: int) -> bool:
        """删除文档索引"""
        try:
            collection_name = f"doc_{document_id}"
            import chromadb
            client = chromadb.PersistentClient(path=self.persist_directory)
            try:
                client.delete_collection(name=collection_name)
                logger.info(f"删除索引成功: {collection_name}")
            except Exception as e:
                logger.warning(f"删除索引时出错（可能不存在）: {str(e)}")
            return True
        except Exception as e:
            logger.error(f"删除索引失败: {str(e)}")
            return False

    def retrieve_documents(self, question: str, index_data: Dict[str, Any], user=None, document=None) -> List[Dict[str, Any]]:
        """检索相关文档片段"""
        try:
            # 获取索引 ID
            collection_name = index_data.get('index_id') if isinstance(index_data, dict) else None
            if not collection_name and document:
                collection_name = f"doc_{document.id}"
            if not collection_name:
                return []

            # 获取模型配置
            model_config = self._get_model_config(user)
            if not model_config:
                return []

            # 导入必要的库
            from langchain_chroma import Chroma

            # 获取 embeddings
            embeddings = self._get_embeddings(model_config)

            # 加载 vector store
            vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name=collection_name
            )

            # 创建检索器
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )

            # 检索相关文档
            source_docs = retriever.invoke(question)

            # 提取来源信息
            sources = []
            for doc in source_docs:
                sources.append({
                    'content': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content,
                    'metadata': doc.metadata
                })

            return sources
        except Exception as e:
            logger.error(f"检索文档失败: {str(e)}")
            return []

    def stream_query(self, question: str, index_data: Dict[str, Any], user=None, document=None):
        """流式查询生成回答"""
        try:
            # 获取索引 ID
            collection_name = index_data.get('index_id') if isinstance(index_data, dict) else None
            if not collection_name and document:
                collection_name = f"doc_{document.id}"
            if not collection_name:
                yield "未找到有效的索引 ID"
                return

            # 获取模型配置
            model_config = self._get_model_config(user)
            if not model_config:
                yield "未找到可用的 AI 模型配置"
                return

            # 导入必要的库
            from langchain_openai import ChatOpenAI
            from langchain_chroma import Chroma
            from langchain_core.prompts import PromptTemplate
            from langchain_core.runnables import RunnablePassthrough

            # 获取 embeddings
            embeddings = self._get_embeddings(model_config)

            # 加载 vector store
            vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name=collection_name
            )

            # 创建检索器
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )

            # 自定义提示模板
            prompt_template = """基于以下文档内容回答问题。如果文档中没有相关信息，请明确说明。

文档内容：
{context}

问题：{question}

请提供准确、简洁的回答："""

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )

            # 使用 LCEL 构建 RAG 链
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            # 获取相关文档
            docs = retriever.invoke(question)
            context = format_docs(docs)

            # 获取 LLM 并启用流式输出
            llm = ChatOpenAI(
                openai_api_key=model_config.get('api_key'),
                openai_api_base=model_config.get('api_base'),
                model_name=model_config.get('model_name', 'gpt-3.5-turbo'),
                temperature=model_config.get('temperature', 0.7),
                streaming=True,
                model_kwargs={
                    'top_p': model_config.get('top_p', 0.9)
                }
            )

            # 构建消息
            from langchain_core.messages import HumanMessage, SystemMessage
            messages = [
                SystemMessage(content="你是一个专业的文档问答助手，基于提供的文档内容回答问题。"),
                HumanMessage(content=PROMPT.format(context=context, question=question))
            ]

            # 流式生成
            for chunk in llm.stream(messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"流式查询失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            yield f"生成回答时出错: {str(e)}"


# 全局服务实例
rag_service = RAGService()
