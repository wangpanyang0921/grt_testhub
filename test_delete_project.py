#!/usr/bin/env python
"""测试项目删除过程，观察用例是否被删除"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
django.setup()

from apps.projects.models import Project
from apps.testcases.models import TestCase
from apps.projects.views import ProjectDetailView
from django.test import RequestFactory

# 获取一个项目
project = Project.objects.first()
if not project:
    print("没有找到项目")
    sys.exit(1)

print(f"项目: {project.name} (ID: {project.id})")

# 记录删除前的用例数量
testcase_ids_before = list(TestCase.objects.filter(project=project).values_list('id', flat=True))
print(f"删除前的用例数量: {len(testcase_ids_before)}")
print(f"删除前的用例 IDs: {testcase_ids_before[:10]}...")  # 只显示前10个

# 模拟删除过程
from django.db import transaction

with transaction.atomic():
    # 先将关联的测试用例的 menu 和 project 字段都设为 null
    updated_count = TestCase.objects.filter(project=project).update(menu=None, project=None)
    print(f"已更新 {updated_count} 个用例的 project 和 menu 为 null")
    
    # 检查更新后的用例
    remaining_testcases = TestCase.objects.filter(id__in=testcase_ids_before)
    print(f"更新后的用例数量: {remaining_testcases.count()}")
    
    # 检查这些用例的 project 和 menu 字段
    for tc in remaining_testcases[:3]:
        print(f"  用例 {tc.id}: project={tc.project}, menu={tc.menu}")
    
    # 删除项目
    project.delete()
    print(f"项目已删除")
    
    # 检查用例是否还存在
    remaining_after_delete = TestCase.objects.filter(id__in=testcase_ids_before)
    print(f"删除项目后的用例数量: {remaining_after_delete.count()}")
    
    if remaining_after_delete.count() != len(testcase_ids_before):
        print(f"警告: 有 {len(testcase_ids_before) - remaining_after_delete.count()} 个用例被删除了！")
    else:
        print("成功: 所有用例都保留了！")
    
    # 回滚事务，不实际删除数据
    raise Exception("测试完成，回滚事务")
