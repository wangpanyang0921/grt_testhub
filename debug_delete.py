#!/usr/bin/env python
"""调试项目删除过程"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
django.setup()

from apps.projects.models import Project
from apps.testcases.models import TestCase
from apps.testsuites.models import TestSuite, TestSuiteCase

def debug_delete():
    # 获取一个项目
    project = Project.objects.first()
    if not project:
        print("没有找到项目")
        return
    
    print(f"项目: {project.name} (ID: {project.id})")
    
    # 获取该项目下的用例
    testcases = TestCase.objects.filter(project=project)
    print(f"关联的用例数量: {testcases.count()}")
    for tc in testcases[:5]:
        print(f"  - {tc.id}: {tc.title[:30]}...")
    
    # 获取该项目下的套件
    testsuites = TestSuite.objects.filter(project=project)
    print(f"关联的套件数量: {testsuites.count()}")
    
    # 获取套件关联的用例
    for suite in testsuites:
        suite_cases = TestSuiteCase.objects.filter(testsuite=suite)
        print(f"  套件 '{suite.name}' 关联的用例数量: {suite_cases.count()}")
    
    print("\n注意：这个脚本只是显示信息，不会删除任何数据")
    print("请在 Django shell 中手动测试删除项目，观察用例是否被删除")

if __name__ == '__main__':
    debug_delete()
