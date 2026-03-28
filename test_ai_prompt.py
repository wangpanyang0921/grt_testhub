#!/usr/bin/env python3
"""
测试AI生成用例时的提示词构建
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
django.setup()

from apps.requirement_analysis.models import TestTemplateConfig, AIModelService

# 测试文本
test_text = "项目工具新增智能体tab，点击显示智能体列表，点击添加知恩你按钮，显示选择智能体抽屉，点击创建智能体，新页签打开跳转智能体列表页面"

print("=" * 80)
print("测试AI提示词构建")
print("=" * 80)

# 测试 _get_matched_template_content 方法
print("\n1. 调用 _get_matched_template_content 方法:")
template_content = AIModelService._get_matched_template_content(test_text)
print(f"   返回内容长度: {len(template_content)} 字符")
print(f"   返回内容:\n{template_content}")

print("\n" + "=" * 80)
