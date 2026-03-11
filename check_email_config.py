#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查邮件配置和通知日志的脚本
"""
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/Users/jinshaomin/Documents/jinsm/test_hub/grt_testhub')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from apps.ui_automation.models import UiNotificationLog, UiScheduledTask, UiTaskNotificationSetting

print("=" * 60)
print("邮件配置检查")
print("=" * 60)

# 1. 检查邮件配置
print("\n1. Django 邮件配置:")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"   EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"   EMAIL_HOST_PASSWORD: {'已设置' if settings.EMAIL_HOST_PASSWORD else '未设置'}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# 2. 检查最近的定时任务
print("\n2. 最近的 UI 定时任务:")
tasks = UiScheduledTask.objects.all().order_by('-updated_at')[:5]
for task in tasks:
    print(f"   ID: {task.id}, 名称: {task.name}")
    print(f"   - notify_on_success: {task.notify_on_success}")
    print(f"   - notify_on_failure: {task.notify_on_failure}")
    print(f"   - notification_type: {task.notification_type}")
    print(f"   - notify_emails: {task.notify_emails}")
    print(f"   - last_run_time: {task.last_run_time}")
    print(f"   - last_result: {task.last_result}")

    # 检查通知设置
    setting = task.notification_settings.first()
    if setting:
        print(f"   - notification_setting.id: {setting.id}")
        print(f"   - notification_setting.is_enabled: {setting.is_enabled}")
        print(f"   - notification_setting.notification_type: {setting.notification_type}")
        print(f"   - notification_setting.notify_on_success: {setting.notify_on_success}")
        print(f"   - notification_setting.notify_on_failure: {setting.notify_on_failure}")
        custom_recipients = list(setting.custom_recipients.values_list('email', flat=True))
        print(f"   - custom_recipients: {custom_recipients}")
    else:
        print(f"   - notification_setting: 无")
    print()

# 3. 检查通知日志
print("\n3. 最近的通知日志:")
logs = UiNotificationLog.objects.all().order_by('-sent_at')[:10]
if logs:
    for log in logs:
        print(f"   任务: {log.task_name}")
        print(f"   - 类型: {log.notification_type}")
        print(f"   - 状态: {log.status}")
        print(f"   - 发送时间: {log.sent_at}")
        print(f"   - 收件人: {log.recipient_info}")
        if log.error_message:
            print(f"   - 错误: {log.error_message}")
        print()
else:
    print("   暂无通知日志")

# 4. 测试邮件发送
print("\n4. 测试邮件发送:")
test_email = input("请输入测试邮箱地址 (直接回车跳过): ").strip()
if test_email:
    try:
        result = send_mail(
            subject='测试邮件 - UI自动化定时任务',
            message='这是一封测试邮件，用于验证邮件配置是否正确。',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print(f"   测试邮件发送成功！发送数量: {result}")
    except Exception as e:
        print(f"   测试邮件发送失败: {str(e)}")
else:
    print("   跳过测试邮件发送")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
