# -*- coding: utf-8 -*-
"""
API Fox 完整导入器 - 100% 兼容
支持 API Fox CLI JSON 格式导入
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from django.db import transaction

from apps.api_testing.models import ApiProject, ApiCollection, ApiRequest, TestSuite, TestSuiteRequest, Environment
from apps.users.models import User
from .apifox_function_mapper import ApifoxVariableResolver, validate_apifox_syntax


class ApifoxImportError(Exception):
    """API Fox 导入错误"""
    pass


class ApifoxCliImporter:
    """
    API Fox CLI JSON 文件导入器
    
    支持功能：
    1. 完整场景导入（包含所有请求、测试步骤）
    2. 100% 变量函数兼容（使用数据工厂）
    3. 环境变量提取（可选）
    4. 前置/后置脚本转换
    5. 变量提取规则转换
    """
    
    def __init__(self, user: User, project: ApiProject):
        self.user = user
        self.project = project
        self.resolver = ApifoxVariableResolver()
        self.import_stats = {
            'collections_created': 0,
            'requests_created': 0,
            'suites_created': 0,
            'variables_converted': 0,
            'warnings': []
        }
    
    def import_from_file(self, file_path: str, 
                         import_env: bool = False,
                         target_collection: ApiCollection = None) -> Dict[str, Any]:
        """
        从 API Fox CLI JSON 文件导入
        
        Args:
            file_path: JSON 文件路径
            import_env: 是否导入环境变量
            target_collection: 指定导入到哪个集合（可选）
        
        Returns:
            导入结果统计
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ApifoxImportError(f"文件读取失败: {str(e)}")
        
        return self.import_from_data(data, import_env, target_collection)
    
    def import_from_data(self, data: Dict[str, Any],
                        import_env: bool = False,
                        target_collection: ApiCollection = None) -> Dict[str, Any]:
        """从数据字典导入"""
        with transaction.atomic():
            # 1. 预处理 - 提取环境变量
            if import_env:
                self._extract_environment(data)
            
            # 2. 创建或获取集合
            collection = target_collection or self._create_collection(data)
            
            # 3. 递归处理所有 items
            items = data.get('item', [])
            requests = self._process_items(items, collection, parent_path='')
            
            # 4. 创建测试套件（自动化场景）
            suite = self._create_test_suite(data, collection, requests)
            
            return {
                'success': True,
                'collection_id': collection.id,
                'suite_id': suite.id if suite else None,
                'stats': self.import_stats,
                'warnings': self.import_stats['warnings']
            }
    
    def _create_collection(self, data: Dict[str, Any]) -> ApiCollection:
        """创建 API 集合"""
        name = data.get('info', {}).get('name', f"API Fox Import {datetime.now().strftime('%Y%m%d')}")
        
        collection = ApiCollection.objects.create(
            project=self.project,
            name=name,
            description=data.get('info', {}).get('description', ''),
            created_by=self.user
        )
        self.import_stats['collections_created'] += 1
        return collection
    
    def _process_items(self, items: List[Dict], collection: ApiCollection, 
                      parent_path: str = '') -> List[ApiRequest]:
        """递归处理 items，创建请求"""
        requests = []
        
        for index, item in enumerate(items):
            item_name = item.get('name', f'Item_{index}')
            current_path = f"{parent_path}/{item_name}" if parent_path else item_name
            
            if 'request' in item:
                # 这是一个请求
                request = self._create_request(item, collection, current_path, index)
                if request:
                    requests.append(request)
            elif 'item' in item:
                # 这是一个文件夹，递归处理
                sub_requests = self._process_items(
                    item['item'], collection, current_path
                )
                requests.extend(sub_requests)
        
        return requests
    
    def _create_request(self, item: Dict, collection: ApiCollection, 
                       path: str, index: int) -> Optional[ApiRequest]:
        """创建 API 请求"""
        request_data = item.get('request', {})
        
        # 解析请求方法
        method = request_data.get('method', 'GET').upper()
        
        # 解析 URL
        url = self._parse_url(request_data.get('url', {}))
        
        # 解析 Headers
        headers = self._parse_headers(request_data.get('header', []))
        
        # 解析 Body
        body = self._parse_body(request_data.get('body', {}))
        
        # 解析 Query 参数
        params = self._parse_query_params(request_data.get('url', {}).get('query', []))
        
        # 转换变量语法
        url = self._convert_variables(url)
        headers = {k: self._convert_variables(v) for k, v in headers.items()}

        # 处理 Body 格式：API Fox 是字符串或对象，TestHub 需要 {type, data} 格式
        if isinstance(body, dict):
            # body 已经是对象（JSON），直接存储
            body = {'type': 'json', 'data': body}
        elif isinstance(body, str) and body:
            # body 是字符串，需要进一步处理
            body_content = self._convert_variables(body)
            # 判断是否是 JSON（去掉变量占位符后再判断）
            try:
                # 先尝试直接解析为对象
                parsed_json = json.loads(body_content)
                body = {'type': 'json', 'data': parsed_json}
            except (json.JSONDecodeError, TypeError):
                # 如果解析失败，可能是包含变量占位符如 ${org_id} 或 ${{func()}}
                # 需要同时检测 API Fox 格式 {{}} 和 TestHub 格式 ${}
                temp_content = body_content
                # 替换 API Fox 格式变量
                temp_content = re.sub(r'\{\{.*?\}\}', '0', temp_content, flags=re.DOTALL)
                # 替换 TestHub 格式变量 ${...}
                temp_content = re.sub(r'\$\{[^}]*\}', '0', temp_content)
                try:
                    json.loads(temp_content)
                    # 去掉变量后是有效的 JSON，标记为 json 类型
                    # 存储原始字符串（包含变量），但标记为 json 类型
                    body = {'type': 'json', 'data': body_content}
                except (json.JSONDecodeError, TypeError):
                    # 确实不是 JSON，作为 raw 处理
                    body = {'type': 'raw', 'data': body_content}
        else:
            body = {}
        
        # 提取事件脚本（前置/后置处理）
        events = item.get('event', [])
        pre_script, post_script, assertions, extractors = self._parse_events(events)
        
        # 创建请求
        request = ApiRequest.objects.create(
            collection=collection,
            name=item.get('name', f'Request_{index}'),
            method=method,
            url=url,
            headers=headers,
            body=body,
            params=params,
            description=item.get('description', ''),
            pre_request_script=pre_script,
            post_request_script=post_script,
            assertions=assertions,
            variable_extractors=extractors,
            created_by=self.user
        )
        
        self.import_stats['requests_created'] += 1
        
        # 存储原始 item 数据（用于测试套件关联）
        request._apifox_item = item
        request._apifox_index = index
        
        return request
    
    def _parse_url(self, url_data: Any) -> str:
        """解析 URL - 只返回路径部分，域名通过环境变量配置"""
        if isinstance(url_data, str):
            # 如果是完整 URL，去掉协议和域名，只保留路径
            if url_data.startswith(('http://', 'https://')):
                # 去掉协议部分
                path_start = url_data.find('://') + 3
                # 从协议后找到第一个 / 的位置
                domain_end = url_data.find('/', path_start)
                if domain_end != -1:
                    return url_data[domain_end:]
                else:
                    return '/'
            return url_data
        
        if isinstance(url_data, dict):
            # 只构建路径部分，去掉 protocol 和 host
            path = '/'.join(url_data.get('path', []))
            if path:
                return '/' + path
            return '/'
        
        return '/'
    
    def _parse_headers(self, headers: List[Dict]) -> Dict[str, str]:
        """解析 Headers - 过滤掉常见的全局 Headers（如 TenantId、Authorization、Content-Type 等）"""
        # 常见的全局 Headers，这些通常在环境管理中统一配置或由 HTTP 客户端自动添加
        global_header_keys = {
            'tenantid', 'authorization', 'x-tenant-id', 'x-auth-token',
            'user-agent', 'content-type', 'accept', 'accept-encoding', 'accept-language',
            'cache-control', 'connection', 'pragma'
        }
        
        result = {}
        for header in headers:
            key = header.get('key', '')
            value = header.get('value', '')
            if key and not header.get('disabled', False):
                # 跳过全局 Headers
                if key.lower() not in global_header_keys:
                    result[key] = value
        return result
    
    def _parse_events(self, events: List[Dict]) -> Tuple[str, str, List[Dict], List[Dict]]:
        """
        解析 API Fox 事件脚本
        
        Returns:
            (pre_request_script, post_request_script, assertions, variable_extractors)
        """
        pre_script_lines = []
        post_script_lines = []
        assertions = []
        extractors = []
        
        for event in events:
            listen = event.get('listen', '')
            script = event.get('script', {})
            exec_lines = script.get('exec', [])
            script_text = '\n'.join(exec_lines)
            
            if listen == 'prerequest':
                # 前置脚本
                pre_script_lines.extend(exec_lines)
            elif listen == 'test':
                # 后置脚本（包含断言和变量提取）
                post_script_lines.extend(exec_lines)
                
                # 提取断言 (pm.expect 或 pm.response.to.have.status)
                assertions.extend(self._extract_assertions(script_text))
                
                # 提取变量提取规则
                extractors.extend(self._extract_variable_extractors(script_text))
        
        return (
            '\n'.join(pre_script_lines),
            '\n'.join(post_script_lines),
            assertions,
            extractors
        )
    
    def _extract_assertions(self, script_text: str) -> List[Dict]:
        """从 API Fox 脚本中提取断言规则"""
        assertions = []

        # API Fox 断言格式分析：
        # 1. pm.test(`断言名称`, ...) - 定义断言名称
        # 2. ____replaceIn(`$.data.path`) - JSONPath 提取路径
        # 3. ____formatValues(..., 'equal') - 比较操作类型
        # 4. compareValue = await ____replaceIn(`{{变量}}`) - 比较值

        # 查找所有的 pm.test 块
        test_pattern = r'pm\.test\(`([^`]+)`[^}]+?try\s*\{([^}]+?(?:const|let)\s+expression[^}]+?)\}\s+catch'

        # 简化处理：按脚本块分割，每个断言是一个独立的 async 块
        # 查找断言名称 (pm.test 中的名称)
        name_pattern = r'const formattedName = await ____replaceIn\(`([^`]+)`\);\s*pm\.test\(`([^`]+)`'
        name_matches = list(re.finditer(name_pattern, script_text))

        # 查找 JSONPath 表达式
        # API Fox 格式: const expression = await ____replaceIn(`$.data.xxx`);
        jsonpath_pattern = r'const expression = await ____replaceIn\(`([^`]+)`\)'
        jsonpath_matches = re.findall(jsonpath_pattern, script_text)

        # 查找比较操作类型
        # ____formatValues(..., 'equal') 或 ____formatValues(..., 'notEmpty')
        op_pattern = r"____formatValues\([^,]+,\s*['\"]([^'\"]+)['\"]\)"
        op_matches = re.findall(op_pattern, script_text)

        # 查找比较值 (如果有)
        compare_pattern = r'const compareValue = await ____replaceIn\(`([^`]+)`\)'
        compare_matches = re.findall(compare_pattern, script_text)

        # 为每个断言创建一个条目
        for i in range(len(name_matches)):
            assertion_name = name_matches[i].group(2)  # pm.test 中的名称
            json_path = jsonpath_matches[i] if i < len(jsonpath_matches) else ''
            op_type = op_matches[i] if i < len(op_matches) else 'equal'
            compare_value = compare_matches[i] if i < len(compare_matches) else None

            # 映射 API Fox 操作类型到 TestHub 类型
            # API Fox 支持的所有断言类型：
            # 等于、不等于、包含、不包含、大于、小于、大于等于、小于等于
            # 为空、不为空、正则匹配、开头是、结尾是、长度等于、长度大于、长度小于
            type_mapping = {
                # 基础比较
                'equal': 'equal',
                '=': 'equal',
                'notEqual': 'not_equal',
                '!=': 'not_equal',
                
                # 包含关系
                'contains': 'contains',
                'notContains': 'not_contains',
                'not_contain': 'not_contains',
                
                # 数值比较
                'greaterThan': 'greater_than',
                '>': 'greater_than',
                'lessThan': 'less_than',
                '<': 'less_than',
                'greaterThanOrEqual': 'greater_than_or_equal',
                '>=': 'greater_than_or_equal',
                'lessThanOrEqual': 'less_than_or_equal',
                '<=': 'less_than_or_equal',
                
                # 空值判断
                'empty': 'empty',
                'notEmpty': 'not_empty',
                'not_empty': 'not_empty',
                
                # 正则匹配
                'regex': 'regex_match',
                'matches': 'regex_match',
                'regexp': 'regex_match',
                
                # 字符串匹配
                'startsWith': 'starts_with',
                'endsWith': 'ends_with',
                
                # 长度比较
                'lengthEqual': 'length_equal',
                'lengthGreaterThan': 'length_greater_than',
                'lengthLessThan': 'length_less_than',
            }

            testhub_type = type_mapping.get(op_type, 'equal')

            assertion = {
                'name': assertion_name,
                'type': testhub_type,
                'source': 'json_body',
                'json_path': json_path,
                'source': 'script'
            }

            # 如果有比较值，添加到断言中
            if compare_value:
                assertion['expected_value'] = compare_value

            assertions.append(assertion)

        # 保留原有的简单断言检测（向后兼容）
        # 匹配 pm.response.to.have.status(code)
        status_pattern = r'pm\.response\.to\.have\.status\((\d+)\)'
        for match in re.finditer(status_pattern, script_text):
            status_code = match.group(1)
            assertions.append({
                'name': f'状态码断言',
                'type': 'status_code',
                'expected': int(status_code),
                'source': 'script'
            })

        return assertions
    
    def _extract_variable_extractors(self, script_text: str) -> List[Dict]:
        """从 API Fox 脚本中提取变量提取规则"""
        extractors = []
        
        # API Fox 格式: ____replaceIn(`变量名`);pm.environment.set(formattedName, value)
        # 找 ____replaceIn 定义变量名和 JSONPath
        var_pattern = r'____replaceIn\(`([^`]+)`\)'
        var_matches = list(re.finditer(var_pattern, script_text))
        
        # API Fox 通常配对出现：第一个是 JSONPath，第二个是变量名
        for i in range(0, len(var_matches), 2):
            if i + 1 < len(var_matches):
                jsonpath = var_matches[i].group(1)
                var_name = var_matches[i + 1].group(1)
                
                # 检查是否是有效的 JSONPath（以 $ 开头）
                if jsonpath.startswith('$'):
                    extractors.append({
                        'name': var_name,
                        'source': 'json_body',
                        'json_path': jsonpath,
                        'variable_name': var_name
                    })
        
        return extractors
    
    def _parse_body(self, body_data: Dict) -> Optional[Union[str, Dict]]:
        """解析请求体 - 返回对象或字符串"""
        mode = body_data.get('mode', 'raw')

        if mode == 'raw':
            raw_content = body_data.get('raw', '')
            # 尝试解析为 JSON 对象
            if raw_content:
                try:
                    # 直接解析
                    return json.loads(raw_content)
                except (json.JSONDecodeError, TypeError):
                    # 如果包含变量占位符，去掉后再尝试解析
                    # 使用非贪婪匹配，支持嵌套括号如 {{$string.alphanumeric(length=4)}}
                    # 注意：API Fox 的变量通常已经被双引号包裹，所以这里用 0 作为占位符
                    temp_content = re.sub(r'\{\{.*?\}\}', '0', raw_content, flags=re.DOTALL)
                    try:
                        json.loads(temp_content)
                        # 去掉变量后是有效的 JSON，说明原始内容应该是 JSON
                        # 但我们无法直接解析，返回原始字符串让上层处理
                        return raw_content
                    except (json.JSONDecodeError, TypeError):
                        # 确实不是 JSON，返回原始字符串
                        return raw_content
            return raw_content
        elif mode == 'json':
            # API Fox 可能使用 json 字段
            json_data = body_data.get('json', '')
            if isinstance(json_data, dict):
                return json_data  # 已经是对象，直接返回
            elif isinstance(json_data, str) and json_data:
                try:
                    return json.loads(json_data)
                except (json.JSONDecodeError, TypeError):
                    return json_data
            return json_data
        elif mode == 'formdata':
            # 表单数据
            formdata = body_data.get('formdata', [])
            return {item['key']: item['value'] for item in formdata if not item.get('disabled')}
        elif mode == 'urlencoded':
            # URL 编码数据
            urlencoded = body_data.get('urlencoded', [])
            return {item['key']: item['value'] for item in urlencoded if not item.get('disabled')}

        return ''
    
    def _parse_query_params(self, query: List[Dict]) -> Dict[str, str]:
        """解析 Query 参数"""
        result = {}
        for param in query:
            key = param.get('key', '')
            value = param.get('value', '')
            if key and not param.get('disabled', False):
                result[key] = value
        return result
    
    def _convert_variables(self, text: str) -> str:
        """转换 API Fox 变量语法到 TestHub 语法
        
        注意：导入时不执行动态函数，保留原始变量语法，让函数在执行时解析
        """
        if not isinstance(text, str):
            return text
        
        # 导入时只转换语法格式，不执行函数
        # API Fox: {{$string.alphanumeric(length=4)}} -> TestHub: ${random_string(4, 'all', 1)}
        # 普通变量: {{variable}} -> ${variable}
        
        # 匹配 API Fox 动态函数 {{$category.function(args)}}
        def replace_func(match):
            func_expr = match.group(1).strip()
            
            # 解析函数名和参数
            if '(' in func_expr:
                func_name = func_expr[:func_expr.index('(')]
                args_str = func_expr[func_expr.index('(')+1:func_expr.rindex(')')]
                
                # 转换为 TestHub 语法
                # $string.alphanumeric -> random_string
                # 注意：func_name 不包含 $ 前缀，因为正则捕获的是 $ 之后的内容
                if func_name == 'string.alphanumeric':
                    # 解析 length 参数
                    length = 10  # 默认值
                    if args_str:
                        try:
                            # 处理 length=4 或 4 格式
                            if '=' in args_str:
                                length = int(args_str.split('=')[1].strip())
                            else:
                                length = int(args_str.strip())
                        except:
                            pass
                    # 使用单引号避免 JSON 解析冲突
                    return "${random_string(" + str(length) + ", 'all', 1)}"
                elif func_name == 'string.numeric':
                    length = 10
                    if args_str:
                        try:
                            if '=' in args_str:
                                length = int(args_str.split('=')[1].strip())
                            else:
                                length = int(args_str.strip())
                        except:
                            pass
                    return "${random_string(" + str(length) + ", 'digits', 1)}"
                elif func_name == 'string.alpha':
                    length = 10
                    if args_str:
                        try:
                            if '=' in args_str:
                                length = int(args_str.split('=')[1].strip())
                            else:
                                length = int(args_str.strip())
                        except:
                            pass
                    return "${random_string(" + str(length) + ", 'letters', 1)}"
                elif func_name == 'string.uuid':
                    return '${random_uuid}'
                else:
                    # 其他函数保留原始格式，让后端运行时处理
                    return f'${{{func_expr}}}'
            else:
                # 无参数函数
                func_name = func_expr
                if func_name == 'timestamp':
                    return '${current_timestamp}'
                elif func_name == 'randomUUID':
                    return '${random_uuid}'
                elif func_name == 'guid':
                    return '${random_uuid}'
                else:
                    return f'${{{func_expr}}}'
        
        # 处理动态函数 {{$function()}} - 转换为 TestHub 动态函数语法
        text = re.sub(r'\{\{\$([^}]+)\}\}', replace_func, text)
        
        # 普通变量 {{variable}}（不以$开头）保持原样不变
        # 这些变量是 API Fox 中提取的变量引用，在自动化场景执行时由 TestHub 处理
        # 注意：不转换为 ${variable}，保持 {{variable}} 格式
        
        return text
    
    def _create_test_suite(self, data: Dict, collection: ApiCollection, 
                          requests: List[ApiRequest]) -> Optional[TestSuite]:
        """创建测试套件（自动化场景）"""
        if not requests:
            return None
        
        # 提取 API Fox 的事件脚本（前置/后置脚本）
        pre_process_script = []
        post_process_script = []
        
        for request in requests:
            item = getattr(request, '_apifox_item', {})
            events = item.get('event', [])
            
            for event in events:
                listen = event.get('listen', '')
                script = event.get('script', {}).get('exec', [])
                
                if listen == 'prerequest':
                    pre_process_script.extend(script)
                elif listen == 'test':
                    post_process_script.extend(script)
        
        # 创建测试套件
        suite = TestSuite.objects.create(
            project=self.project,
            name=data.get('info', {}).get('name', f"Suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            description=data.get('info', {}).get('description', ''),
            created_by=self.user,
            pre_process_script='\n'.join(pre_process_script),
            post_process_script='\n'.join(post_process_script)
        )
        
        # 关联请求到套件
        for index, request in enumerate(requests):
            TestSuiteRequest.objects.create(
                test_suite=suite,
                request=request,
                order=index + 1,
                extracted_variables=self._extract_variables_from_script(
                    getattr(request, '_apifox_item', {})
                )
            )
        
        self.import_stats['suites_created'] += 1
        return suite
    
    def _extract_variables_from_script(self, item: Dict) -> Dict[str, str]:
        """从测试脚本中提取变量定义"""
        variables = {}
        events = item.get('event', [])
        
        for event in events:
            if event.get('listen') == 'test':
                script = event.get('script', {}).get('exec', [])
                script_text = '\n'.join(script)
                
                # 提取 pm.environment.set("key", value) 格式
                set_pattern = r'pm\.environment\.set\(["\']([^"\']+)["\']\s*,\s*([^)]+)\)'
                for match in re.finditer(set_pattern, script_text):
                    key = match.group(1)
                    # 尝试提取 JSONPath
                    jsonpath_pattern = r'json\[\'([^\']+)\'\]|json\.([a-zA-Z_]+)'
                    jsonpath_matches = re.findall(jsonpath_pattern, match.group(2))
                    if jsonpath_matches:
                        jsonpath = jsonpath_matches[0][0] or jsonpath_matches[0][1]
                        variables[key] = f"$.{jsonpath}"
        
        return variables
    
    def _extract_environment(self, data: Dict) -> None:
        """提取环境变量（不创建环境，仅记录）"""
        # API Fox 环境变量可能在变量定义中
        variables = data.get('variable', [])
        
        for var in variables:
            if not var.get('disabled', False):
                name = var.get('key', '')
                value = var.get('value', '')
                
                # 验证变量语法
                validation = validate_apifox_syntax(value)
                if not validation['valid']:
                    self.import_stats['warnings'].append(
                        f"环境变量 '{name}' 包含不支持的函数: {validation['unsupported']}"
                    )
    
    def validate_import(self, file_path: str) -> Dict[str, Any]:
        """
        验证导入文件，检查兼容性
        
        Returns:
            {
                'valid': bool,
                'unsupported_functions': List[str],
                'total_requests': int,
                'warnings': List[str]
            }
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'unsupported_functions': [],
                'total_requests': 0,
                'warnings': []
            }
        
        # 收集所有用到的函数
        all_text = json.dumps(data)
        unsupported = []
        
        # 提取所有 {{$...}} 语法
        pattern = r'\{\{\$([^}|]+?)\}'
        matches = re.findall(pattern, all_text)
        
        supported = self.resolver.mapper.get_supported_functions()
        
        for match in matches:
            if '(' in match:
                func_name = '$' + match[:match.index('(')]
            else:
                func_name = '$' + match
            
            if func_name not in supported and func_name not in unsupported:
                unsupported.append(func_name)
        
        # 统计请求数量
        total_requests = self._count_requests(data.get('item', []))
        
        return {
            'valid': len(unsupported) == 0,
            'unsupported_functions': unsupported,
            'total_requests': total_requests,
            'warnings': [f"发现 {len(unsupported)} 个不支持的函数"] if unsupported else []
        }
    
    def _count_requests(self, items: List[Dict]) -> int:
        """统计请求数量"""
        count = 0
        for item in items:
            if 'request' in item:
                count += 1
            elif 'item' in item:
                count += self._count_requests(item['item'])
        return count


# 便捷函数
def import_apifox_cli(file_path: str, user: User, project: ApiProject,
                     import_env: bool = False) -> Dict[str, Any]:
    """
    便捷函数：导入 API Fox CLI 文件
    
    使用示例:
        result = import_apifox_cli(
            file_path='智能体_创建.apifox-cli.json',
            user=request.user,
            project=project
        )
    """
    importer = ApifoxCliImporter(user, project)
    return importer.import_from_file(file_path, import_env)


def validate_apifox_file(file_path: str) -> Dict[str, Any]:
    """
    便捷函数：验证 API Fox 文件
    
    使用示例:
        validation = validate_apifox_file('智能体_创建.apifox-cli.json')
        if not validation['valid']:
            print(f"不支持的函数: {validation['unsupported_functions']}")
    """
    importer = ApifoxCliImporter(None, None)
    return importer.validate_import(file_path)
