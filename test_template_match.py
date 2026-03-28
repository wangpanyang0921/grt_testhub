#!/usr/bin/env python3
"""
测试模板匹配逻辑
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
django.setup()

from apps.requirement_analysis.models import TestTemplateConfig

# 测试文本
test_text = "项目工具新增智能体tab，点击显示智能体列表，点击添加知恩你按钮，显示选择智能体抽屉，点击创建智能体，新页签打开跳转智能体列表页面"

print("=" * 80)
print("测试模板匹配")
print("=" * 80)
print(f"\n测试文本: {test_text[:50]}...")
print()

# 测试匹配所有类型的模板
print("1. 匹配所有启用的模板:")
all_templates = TestTemplateConfig.objects.filter(is_active=True)
print(f"   数据库中共有 {all_templates.count()} 个启用的模板")

# 测试匹配测试点模板
print("\n2. 匹配测试点模板:")
matched_test_points = TestTemplateConfig.match_templates(test_text, 'test_point')
print(f"   匹配到 {len(matched_test_points)} 个测试点模板")
for template in matched_test_points:
    print(f"   - {template.name} (关键词: {template.get_keywords_list()})")
    print(f"     内容: {template.content}")

# 测试 get_test_points 方法
print("\n3. 调用 get_test_points 方法:")
test_points = TestTemplateConfig.get_test_points(test_text)
print(f"   获取到 {len(test_points)} 个测试点")
for i, point in enumerate(test_points, 1):
    print(f"   {i}. {point}")

# 测试匹配测试场景模板
print("\n4. 匹配测试场景模板:")
matched_scenarios = TestTemplateConfig.match_templates(test_text, 'test_scenario')
print(f"   匹配到 {len(matched_scenarios)} 个测试场景模板")
for template in matched_scenarios:
    print(f"   - {template.name} (关键词: {template.get_keywords_list()})")

# 测试 get_test_scenarios 方法
print("\n5. 调用 get_test_scenarios 方法:")
test_scenarios = TestTemplateConfig.get_test_scenarios(test_text)
print(f"   获取到 {len(test_scenarios)} 个测试场景")
for i, scenario in enumerate(test_scenarios, 1):
    print(f"   {i}. {scenario}")

# 测试关键词匹配逻辑
print("\n6. 关键词匹配详情:")
text_lower = test_text.lower()
for template in all_templates:
    keywords = template.get_keywords_list()
    matched_keywords = [k for k in keywords if k.lower() in text_lower]
    if matched_keywords:
        print(f"   模板 '{template.name}' 匹配到关键词: {matched_keywords}")

print("\n" + "=" * 80)
