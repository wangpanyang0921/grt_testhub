# -*- coding: utf-8 -*-
"""
AI断言生成服务

基于API响应内容，使用AI自动生成测试断言。
支持状态码、JSON路径、响应内容等多种断言类型。
"""

import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from django.conf import settings

from apps.requirement_analysis.models import AIModelConfig, PromptConfig

logger = logging.getLogger(__name__)


class AIAssertionGenerator:
    """AI断言生成器"""

    # 默认系统提示词 - 当没有配置时使用
    # 支持变量：
    #   {{response_time_threshold}} - 响应时间阈值（毫秒），默认5000
    DEFAULT_SYSTEM_PROMPT = """你是一个专业的API测试专家。请基于提供的API响应数据，生成合适的测试断言。

生成的断言需要满足以下要求：
1. 覆盖关键字段的验证（如状态码、success字段、data关键字段）
2. 使用合适的断言类型（status_code、json_path、contains等）
3. 断言条件应该合理，基于实际响应值
4. 每个断言应该有清晰的名称说明验证目的
5. 返回JSON数组格式

支持的断言类型：
- status_code: 验证HTTP状态码
- json_path: 验证JSON路径提取的值
- contains: 验证响应内容包含特定文本
- response_time: 验证响应时间（默认<{{response_time_threshold}}ms）

返回格式必须是JSON数组，每个元素包含：
- name: 断言名称
- type: 断言类型
- expected: 预期值
- json_path: JSON路径（仅json_path类型需要）

示例输出：
[
  {"name": "状态码验证", "type": "status_code", "expected": 200},
  {"name": "响应时间小于5.0秒", "type": "response_time", "expected": 5000},
  {"name": "返回成功标识", "type": "json_path", "json_path": "$.success", "expected": "true"},
  {"name": "返回码验证", "type": "json_path", "json_path": "$.code", "expected": "00000"},
  {"name": "data.access_token存在", "type": "json_path", "json_path": "$.data.access_token", "expected": "exist"}
]"""

    @staticmethod
    def _get_active_model_config() -> Optional[AIModelConfig]:
        """获取当前激活的AI模型配置（专门用于断言生成）"""
        try:
            # 只查找 assertion_generator 角色的激活配置
            config = AIModelConfig.objects.filter(
                role='assertion_generator',
                is_active=True
            ).first()
            if config:
                logger.info(f"使用断言生成专用模型配置: {config.name}")
            else:
                logger.info("未找到断言生成专用模型配置，将使用本地规则生成")
            return config
        except Exception as e:
            logger.error(f"获取AI模型配置失败: {e}")
            return None

    @staticmethod
    def _get_system_prompt(response_time_threshold: int = 5000) -> str:
        """获取系统提示词，优先使用配置中的提示词
        
        Args:
            response_time_threshold: 响应时间阈值（毫秒），默认5000
        """
        prompt_content = None
        
        try:
            # 从PromptConfig获取断言生成类型的提示词
            prompt_config = PromptConfig.get_active_config('assertion_generator')
            if prompt_config and prompt_config.content:
                logger.info(f"使用配置的断言生成提示词: {prompt_config.name}")
                prompt_content = prompt_config.content
        except Exception as e:
            logger.warning(f"获取配置的提示词失败: {e}")

        # 如果没有配置或获取失败，使用默认提示词
        if not prompt_content:
            prompt_content = AIAssertionGenerator.DEFAULT_SYSTEM_PROMPT
        
        # 替换变量
        prompt_content = prompt_content.replace('{{response_time_threshold}}', str(response_time_threshold))
        
        return prompt_content

    @staticmethod
    def _call_openai_compatible_api(config: AIModelConfig, messages: List[Dict[str, str]]) -> str:
        """调用OpenAI兼容格式的API"""
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': config.model_name,
            'messages': messages,
            'max_tokens': min(config.max_tokens, 2000),
            'temperature': 0.3,  # 使用较低温度获得更确定性的结果
            'stream': False
        }

        # 构建API URL
        base_url = config.base_url.rstrip('/')
        if not base_url.endswith('/chat/completions'):
            if base_url.endswith('/v1'):
                url = f"{base_url}/chat/completions"
            else:
                url = f"{base_url}/v1/chat/completions"
        else:
            url = base_url

        try:
            response = httpx.post(url, headers=headers, json=data, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"AI API调用失败: {e}")
            raise Exception(f"AI服务调用失败: {str(e)}")

    @staticmethod
    def _extract_json_from_response(content: str) -> List[Dict]:
        """从AI响应中提取JSON数据"""
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从代码块中提取
        import re

        # 匹配 ```json ... ``` 或 ``` ... ``` 格式
        patterns = [
            r'```json\s*(\[.*?\])\s*```',
            r'```\s*(\[.*?\])\s*```',
            r'(\[\s*\{.*?\}\s*\])'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        raise ValueError("无法从AI响应中解析出有效的JSON断言数据")

    @staticmethod
    def generate_assertions(
        status_code: int,
        response_body: Any,
        response_headers: Optional[Dict] = None,
        response_time: Optional[float] = None,
        response_time_threshold: int = 5000
    ) -> List[Dict[str, Any]]:
        """
        基于响应数据生成断言

        Args:
            status_code: HTTP状态码
            response_body: 响应体（可以是JSON对象或字符串）
            response_headers: 响应头
            response_time: 响应时间（毫秒）
            response_time_threshold: 响应时间阈值（毫秒），默认5000

        Returns:
            断言列表
        """
        # 获取AI配置
        config = AIAssertionGenerator._get_active_model_config()
        if not config:
            logger.warning("未找到激活的AI模型配置，使用默认规则生成断言")
            return AIAssertionGenerator._generate_default_assertions(
                status_code, response_body, response_time, response_time_threshold
            )

        # 准备响应数据描述
        response_summary = AIAssertionGenerator._prepare_response_summary(
            status_code, response_body, response_headers, response_time
        )

        # 获取系统提示词（优先使用配置），并传入变量
        system_prompt = AIAssertionGenerator._get_system_prompt(response_time_threshold)

        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请为以下API响应生成测试断言：\n\n{response_summary}"}
        ]

        try:
            # 调用AI服务
            ai_response = AIAssertionGenerator._call_openai_compatible_api(config, messages)

            # 解析AI响应
            assertions = AIAssertionGenerator._extract_json_from_response(ai_response)

            # 验证并清理断言
            assertions = AIAssertionGenerator._validate_assertions(assertions)

            logger.info(f"AI成功生成 {len(assertions)} 个断言")
            return assertions

        except Exception as e:
            logger.error(f"AI断言生成失败: {e}")
            # 失败时回退到默认规则
            return AIAssertionGenerator._generate_default_assertions(
                status_code, response_body, response_time, response_time_threshold
            )

    @staticmethod
    def _prepare_response_summary(
        status_code: int,
        response_body: Any,
        response_headers: Optional[Dict],
        response_time: Optional[float]
    ) -> str:
        """准备响应数据摘要"""
        summary_parts = []

        # 状态码
        summary_parts.append(f"HTTP状态码: {status_code}")

        # 响应时间
        if response_time:
            summary_parts.append(f"响应时间: {response_time:.2f}ms")

        # 响应头
        if response_headers:
            content_type = response_headers.get('content-type', '')
            summary_parts.append(f"Content-Type: {content_type}")

        # 响应体
        if isinstance(response_body, dict):
            summary_parts.append(f"响应体 (JSON):\n{json.dumps(response_body, ensure_ascii=False, indent=2)}")
        elif isinstance(response_body, str):
            # 尝试解析为JSON
            try:
                parsed = json.loads(response_body)
                summary_parts.append(f"响应体 (JSON):\n{json.dumps(parsed, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError:
                # 非JSON，截取部分内容
                preview = response_body[:500] + "..." if len(response_body) > 500 else response_body
                summary_parts.append(f"响应体 (文本):\n{preview}")
        else:
            summary_parts.append(f"响应体: {str(response_body)}")

        return "\n\n".join(summary_parts)

    @staticmethod
    def _validate_assertions(assertions: List[Dict]) -> List[Dict]:
        """验证并清理断言数据"""
        valid_types = {
            'status_code', 'json_path', 'contains', 'response_time',
            'header', 'equals', 'not_empty', 'empty'
        }

        validated = []
        for assertion in assertions:
            if not isinstance(assertion, dict):
                continue

            # 检查必需字段
            if 'type' not in assertion:
                continue

            assertion_type = assertion.get('type', '')

            # 标准化类型名称
            if assertion_type == 'statusCode' or assertion_type == 'status':
                assertion_type = 'status_code'
            elif assertion_type == 'jsonPath':
                assertion_type = 'json_path'
            elif assertion_type == 'responseTime':
                assertion_type = 'response_time'

            if assertion_type not in valid_types:
                continue

            # 构建标准格式的断言
            cleaned = {
                'name': assertion.get('name', f'断言 {len(validated) + 1}'),
                'type': assertion_type
            }

            # 根据类型添加特定字段
            if assertion_type == 'status_code':
                cleaned['expected'] = int(assertion.get('expected', 200))
            elif assertion_type == 'response_time':
                cleaned['expected'] = int(assertion.get('expected', 5000))
            elif assertion_type == 'json_path':
                cleaned['json_path'] = assertion.get('json_path', assertion.get('jsonPath', ''))
                expected = assertion.get('expected', '')
                # 处理特殊值
                if expected == 'exist':
                    cleaned['type'] = 'not_empty'
                elif expected == 'not_exist':
                    cleaned['type'] = 'empty'
                else:
                    cleaned['expected'] = str(expected)
            elif assertion_type == 'contains':
                cleaned['expected'] = str(assertion.get('expected', ''))
            elif assertion_type == 'header':
                cleaned['header_name'] = assertion.get('header_name', '')
                cleaned['expected_value'] = str(assertion.get('expected_value', ''))
            else:
                # 其他类型，保留expected
                if 'expected' in assertion:
                    cleaned['expected'] = assertion['expected']

            validated.append(cleaned)

        return validated

    @staticmethod
    def _generate_default_assertions(
        status_code: int,
        response_body: Any,
        response_time: Optional[float],
        response_time_threshold: int = 5000
    ) -> List[Dict[str, Any]]:
        """
        使用默认规则生成断言（当AI不可用时回退使用）
        """
        assertions = []

        # 1. 状态码断言
        assertions.append({
            'name': '状态码验证',
            'type': 'status_code',
            'expected': status_code
        })

        # 2. 响应时间断言
        if response_time:
            seconds = response_time_threshold / 1000
            assertions.append({
                'name': f'响应时间小于{seconds}秒',
                'type': 'response_time',
                'expected': response_time_threshold
            })

        # 3. 尝试解析JSON并生成断言
        json_data = None
        if isinstance(response_body, dict):
            json_data = response_body
        elif isinstance(response_body, str):
            try:
                json_data = json.loads(response_body)
            except json.JSONDecodeError:
                pass

        if json_data:
            # 检查常见的成功标识字段
            if 'success' in json_data:
                assertions.append({
                    'name': '返回成功标识',
                    'type': 'json_path',
                    'json_path': '$.success',
                    'expected': str(json_data['success'])
                })

            if 'code' in json_data:
                assertions.append({
                    'name': '返回码验证',
                    'type': 'json_path',
                    'json_path': '$.code',
                    'expected': str(json_data['code'])
                })

            # 为data下的第一层字段生成存在性断言
            if 'data' in json_data and isinstance(json_data['data'], dict):
                for key in list(json_data['data'].keys())[:3]:  # 最多3个字段
                    value = json_data['data'][key]
                    if value is not None:
                        if isinstance(value, (str, int, float, bool)):
                            assertions.append({
                                'name': f'data.{key}字段验证',
                                'type': 'json_path',
                                'json_path': f'$.data.{key}',
                                'expected': str(value)
                            })
                        else:
                            assertions.append({
                                'name': f'data.{key}字段存在',
                                'type': 'json_path',
                                'json_path': f'$.data.{key}',
                                'expected': 'exist'
                            })

        return assertions
