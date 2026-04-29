"""
变量提取工具模块
用于从响应中提取数据并保存到环境变量
"""
import json
import re
from typing import Any, Dict, List, Optional


def extract_json_value(data: Any, json_path: str) -> Any:
    """
    从 JSON 数据中提取值
    支持简单的 JSON Path 表达式，如: $.data.token, $.data[0].id
    """
    if not json_path or not json_path.startswith('$'):
        return None

    # 移除 $ 前缀
    path = json_path[1:]
    if not path:
        return data

    current = data

    # 解析路径
    # 支持 .key 和 [index] 两种格式
    pattern = r'\.(\w+)|\[(\d+)\]'
    matches = re.findall(pattern, path)

    for match in matches:
        key, index = match
        if key:
            # 对象属性访问
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        elif index:
            # 数组索引访问
            idx = int(index)
            if isinstance(current, list) and 0 <= idx < len(current):
                current = current[idx]
            else:
                return None

    return current


def extract_header_value(headers: Dict[str, str], header_name: str) -> Optional[str]:
    """
    从响应头中提取值
    支持大小写不敏感匹配
    """
    if not headers or not header_name:
        return None

    # 首先尝试精确匹配
    if header_name in headers:
        return headers[header_name]

    # 尝试大小写不敏感匹配
    header_name_lower = header_name.lower()
    for key, value in headers.items():
        if key.lower() == header_name_lower:
            return value

    return None


def extract_variables(
    response_body: Any,
    response_headers: Dict[str, str],
    extractors: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    根据提取规则从响应中提取变量

    Args:
        response_body: 响应体（已解析为 Python 对象）
        response_headers: 响应头字典
        extractors: 提取规则列表

    Returns:
        提取的变量字典 {variable_name: extracted_value}
    """
    extracted_vars = {}
    extraction_results = []

    for extractor in extractors:
        name = extractor.get('name', '未命名')
        source = extractor.get('source', 'json_body')
        variable_name = extractor.get('variable_name', '')

        if not variable_name:
            extraction_results.append({
                'name': name,
                'success': False,
                'error': '变量名称为空',
                'variable_name': variable_name
            })
            continue

        try:
            if source == 'json_body':
                json_path = extractor.get('json_path', '')
                if not json_path:
                    extraction_results.append({
                        'name': name,
                        'success': False,
                        'error': 'JSON Path 为空',
                        'variable_name': variable_name
                    })
                    continue

                value = extract_json_value(response_body, json_path)
                if value is not None:
                    extracted_vars[variable_name] = value
                    extraction_results.append({
                        'name': name,
                        'success': True,
                        'json_path': json_path,
                        'variable_name': variable_name,
                        'value': value
                    })
                else:
                    extraction_results.append({
                        'name': name,
                        'success': False,
                        'error': f'JSON Path "{json_path}" 未找到值',
                        'json_path': json_path,
                        'variable_name': variable_name
                    })

            elif source == 'header':
                header_name = extractor.get('header_name', '')
                if not header_name:
                    extraction_results.append({
                        'name': name,
                        'success': False,
                        'error': '响应头名称为空',
                        'variable_name': variable_name
                    })
                    continue

                value = extract_header_value(response_headers, header_name)
                if value is not None:
                    extracted_vars[variable_name] = value
                    extraction_results.append({
                        'name': name,
                        'success': True,
                        'header_name': header_name,
                        'variable_name': variable_name,
                        'value': value
                    })
                else:
                    extraction_results.append({
                        'name': name,
                        'success': False,
                        'error': f'响应头 "{header_name}" 未找到',
                        'header_name': header_name,
                        'variable_name': variable_name
                    })

        except Exception as e:
            extraction_results.append({
                'name': name,
                'success': False,
                'error': str(e),
                'variable_name': variable_name
            })

    return {
        'variables': extracted_vars,
        'results': extraction_results
    }


def save_variables_to_environment(
    environment_id: int,
    variables: Dict[str, Any],
    user
) -> bool:
    """
    保存变量到环境

    Args:
        environment_id: 环境ID
        variables: 要保存的变量字典
        user: 当前用户

    Returns:
        是否保存成功
    """
    from .models import Environment

    try:
        env = Environment.objects.get(id=environment_id)
        # 将提取的变量转换为对象格式，默认 isHeader 为 false
        formatted_variables = {}
        for key, value in variables.items():
            formatted_variables[key] = {
                'initialValue': str(value) if value is not None else '',
                'currentValue': str(value) if value is not None else '',
                'isHeader': False  # 提取生成的变量默认关闭可被接口引用
            }
        # 更新环境变量
        env.variables.update(formatted_variables)
        env.save()
        return True
    except Environment.DoesNotExist:
        return False
    except Exception as e:
        print(f"保存环境变量失败: {e}")
        return False
