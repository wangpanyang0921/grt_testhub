#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试断言变量转换逻辑"""

import re

def convert_assertion_value(value):
    """将 ${...} 格式转换为 {{...}} 格式"""
    if not isinstance(value, str):
        return value
    # 支持 ${$.N.xxx}、${$N.xxx}、${.N.xxx} 等格式
    original = value
    result = re.sub(r'\$\{(\$[^}]+)\}', r'{{\1}}', value)
    if original != result:
        print(f"DEBUG - 断言值格式转换: '{original}' -> '{result}'")
    return result

def convert_step_reference_with_warning(text, apifox_to_request_index, current_order=None):
    """转换跨步骤变量引用"""
    if not text or not isinstance(text, str):
        return text, None
    
    # 匹配跨步骤引用: {{$.数字.request.xxx}} 或 {{$..数字.request.xxx}}
    # 同时支持 * 通配符表示上一个步骤
    pattern = r'\{\{\$\.?(\d+|\*)\.(request|response)\.(body|headers|params)(?:\.(.*))?\}\}'
    
    warning = None
    
    def replace_ref(match):
        nonlocal warning
        idx_str = match.group(1)
        rest = match.group(2) + '.' + match.group(3)
        if match.group(4):
            rest += '.' + match.group(4)
        
        # 处理 * 通配符
        if idx_str == '*':
            if current_order is not None and current_order > 1:
                prev_order = current_order - 1
                result = f'{{{{$.{prev_order}.{rest}}}}}'
                print(f"DEBUG - 转换通配符引用: * -> TestHub[{prev_order}]: {result}")
                return result
            else:
                return match.group(0)
        
        # 处理数字索引
        apifox_idx = int(idx_str)
        
        if apifox_idx in apifox_to_request_index:
            testhub_order = apifox_to_request_index[apifox_idx]
            result = f'{{{{$.{testhub_order}.{rest}}}}}'
            print(f"DEBUG - 转换变量引用: Apifox[{apifox_idx}] -> TestHub[{testhub_order}]: {result}")
            return result
        else:
            print(f"WARNING - 找不到 Apifox 索引 {apifox_idx} 的映射")
            return match.group(0)
    
    result = re.sub(pattern, replace_ref, text)
    return result, warning


# 模拟测试
print("=" * 60)
print("测试断言变量转换")
print("=" * 60)

# 模拟映射表（根据截图，索引 5 应该映射到步骤 5）
apifox_to_request_index = {
    0: 1,  # 登录_获取Token
    1: 2,  # 组织架构_组织树
    2: 3,  # 智能体_创建
    3: 4,  # 智能体_查询
    4: 5,  # 智能体_创建标注
    5: 6,  # 查询标注（当前步骤）
}

# 测试断言转换
test_cases = [
    # 原始值, 当前步骤号
    ("${$.5.request.body.question_content}", 6),
    ("{{$.5.request.body.question_content}}", 6),
    ("${$.*.request.body.xxx}", 6),
]

print("\n映射表:", apifox_to_request_index)
print()

for original, current_order in test_cases:
    print(f"\n测试: '{original}' (current_order={current_order})")
    print("-" * 40)
    
    # 步骤1: 格式转换
    step1 = convert_assertion_value(original)
    print(f"步骤1 - 格式转换: '{step1}'")
    
    # 步骤2: 索引映射
    step2, _ = convert_step_reference_with_warning(step1, apifox_to_request_index, current_order)
    print(f"步骤2 - 索引映射: '{step2}'")
    
    print(f"最终结果: '{step2}'")
