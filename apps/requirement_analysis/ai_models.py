# -*- coding: utf-8 -*-
"""
AI模型服务
注意：模型定义已移至 models.py，此文件仅保留服务类
"""
import json
import httpx
import asyncio
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# 从 models.py 导入模型
from .models import AIModelConfig, PromptConfig, TestCaseGenerationTask, TestTemplateConfig


class AIModelService:
    """AI模型服务类"""

    @staticmethod
    async def _get_matched_template_content(requirement_text: str) -> str:
        """
        获取匹配到的模板内容，用于追加到AI生成提示词中（异步版本）
        从 models.py 复制此方法来保持一致性
        """
        try:
            # 使用 sync_to_async 包装 ORM 调用，避免在异步上下文中直接调用
            from asgiref.sync import sync_to_async

            # 获取匹配的测试点模板
            get_test_points_sync = sync_to_async(TestTemplateConfig.get_test_points, thread_sensitive=True)
            test_points = await get_test_points_sync(requirement_text)

            # 获取匹配的测试场景模板
            get_test_scenarios_sync = sync_to_async(TestTemplateConfig.get_test_scenarios, thread_sensitive=True)
            test_scenarios = await get_test_scenarios_sync(requirement_text)

            template_sections = []

            # 添加测试点
            if test_points:
                template_sections.append("【必须包含的测试点】")
                template_sections.append("以下测试点来自系统模板配置，必须在生成的用例中覆盖：")
                for i, point in enumerate(test_points, 1):
                    template_sections.append(f"{i}. {point}")
                template_sections.append("")

            # 添加测试场景
            if test_scenarios:
                template_sections.append("【必须包含的测试场景】")
                template_sections.append("以下测试场景来自系统模板配置，必须在生成的用例中覆盖：")
                for i, scenario in enumerate(test_scenarios, 1):
                    template_sections.append(f"{i}. {scenario}")
                template_sections.append("")

            if template_sections:
                template_sections.append("【重要】以上模板配置的测试点和场景必须包含在最终生成的测试用例中，不能遗漏。")
                return "\n".join(template_sections)

            return ""
        except Exception as e:
            logger.warning(f"获取匹配模板内容时出错: {e}")
            return ""

    @staticmethod
    async def call_openai_compatible_api(config: AIModelConfig, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """调用OpenAI兼容格式的API"""
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': config.model_name,
            'messages': messages,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature,
            'top_p': config.top_p,
            'stream': False
        }

        # 确保base_url不以/结尾
        base_url = config.base_url.rstrip('/')
        # 如果用户没有输入完整的v1/chat/completions路径，尝试智能补全
        if not base_url.endswith('/chat/completions'):
            if base_url.endswith('/v1'):
                url = f"{base_url}/chat/completions"
            else:
                # 默认假设是根路径，尝试添加 v1/chat/completions
                # 但对于某些API（如DeepSeek），base_url可能已经是 https://api.deepseek.com
                url = f"{base_url}/v1/chat/completions"
        else:
            url = base_url

        try:
            # Increase timeout to 120s for long generation tasks
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data
                )

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"API调用返回错误: Status={response.status_code}, Body={error_detail}")

                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            provider_name = config.get_model_type_display()
            error_msg = f"{provider_name} API返回错误 {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except httpx.TimeoutException as e:
            provider_name = config.get_model_type_display()
            logger.error(f"{provider_name} API请求超时: {repr(e)}")
            raise Exception(f"{provider_name} API请求超时，请稍后再试或检查网络连接")
        except Exception as e:
            provider_name = config.get_model_type_display()
            # Use repr(e) to capture the full exception type and message, especially if str(e) is empty
            logger.error(f"{provider_name} API调用失败: {repr(e)}")
            raise Exception(f"{provider_name} API调用失败: {str(e) or repr(e)}")

    @staticmethod
    async def call_deepseek_api(config: AIModelConfig, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """调用DeepSeek API (兼容OpenAI格式)"""
        return await AIModelService.call_openai_compatible_api(config, messages)

    @staticmethod
    async def call_qwen_api(config: AIModelConfig, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """调用千问API (兼容OpenAI格式)"""
        return await AIModelService.call_openai_compatible_api(config, messages)

    @staticmethod
    async def generate_test_cases(task: TestCaseGenerationTask) -> str:
        """生成测试用例"""
        writer_prompt = task.writer_prompt_config.content

        # 获取匹配的模板内容
        template_content = await AIModelService._get_matched_template_content(task.requirement_text)
        if template_content:
            logger.info(f"ai_models: 需求文本匹配到模板内容，将追加到生成提示词中")

        # 构建用户提示
        user_message = f"请深入分析以下需求文档，并设计高覆盖率的测试用例。\n\n"

        # 优先追加模板内容（如果存在），放在最前面强调其重要性
        if template_content:
            user_message += f"🚨🚨🚨【最高优先级 - 系统强制要求】🚨🚨🚨\n"
            user_message += f"{template_content}\n"
            user_message += f"🚨🚨🚨【以上测试点和场景必须100%包含在输出中，不得遗漏】🚨🚨🚨\n\n"

        user_message += f"【需求文档内容】\n{task.requirement_text}"

        messages = [
            {"role": "system", "content": writer_prompt},
            {"role": "user", "content": user_message}
        ]

        # 所有支持的模型都使用兼容OpenAI的接口
        response = await AIModelService.call_openai_compatible_api(task.writer_model_config, messages)

        return response['choices'][0]['message']['content']

    @staticmethod
    async def review_test_cases(task: TestCaseGenerationTask, test_cases: str) -> str:
        """评审测试用例"""
        reviewer_prompt = task.reviewer_prompt_config.content
        user_message = f"请评审以下测试用例：\n\n{test_cases}"

        messages = [
            {"role": "system", "content": reviewer_prompt},
            {"role": "user", "content": user_message}
        ]

        # 所有支持的模型都使用兼容OpenAI的接口
        response = await AIModelService.call_openai_compatible_api(task.reviewer_model_config, messages)

        return response['choices'][0]['message']['content']
