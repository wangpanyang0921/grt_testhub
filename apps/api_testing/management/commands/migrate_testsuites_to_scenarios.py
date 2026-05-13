"""
迁移命令：将 TestSuite 数据迁移到 AutomationScenario

用法：
    python manage.py migrate_testsuites_to_scenarios
    python manage.py migrate_testsuites_to_scenarios --dry-run  # 仅预览，不实际迁移
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.api_testing.models import TestSuite, TestSuiteRequest, TestSuiteReviewRecord
from apps.api_testing.models import AutomationScenario, ScenarioStep, ScenarioReviewRecord
from apps.api_testing.models import ApiRequest


class Command(BaseCommand):
    help = '将 TestSuite 数据迁移到 AutomationScenario'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅预览迁移内容，不实际写入数据库',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('=== 试运行模式，不会修改数据库 ==='))

        # 获取所有未迁移的 TestSuite
        test_suites = TestSuite.objects.filter(scenario__isnull=True)
        total = test_suites.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS('没有需要迁移的 TestSuite'))
            return

        self.stdout.write(f'发现 {total} 个需要迁移的 TestSuite')

        migrated = 0
        failed = 0

        for suite in test_suites:
            try:
                with transaction.atomic():
                    if not dry_run:
                        self.migrate_suite(suite)
                    migrated += 1
                    self.stdout.write(f'  ✓ {suite.name}')
            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(f'  ✗ {suite.name}: {str(e)}'))

        if dry_run:
            self.stdout.write(self.style.WARNING(f'\n=== 试运行完成，{migrated} 个可迁移 ==='))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n迁移完成: {migrated} 个成功, {failed} 个失败'))

    def migrate_suite(self, suite):
        """迁移单个 TestSuite"""
        # 1. 创建 AutomationScenario
        scenario = AutomationScenario.objects.create(
            project=suite.project,
            name=suite.name,
            description=suite.description or '',
            environment=suite.environment,
            global_variables={},
            pre_script='',
            post_script='',
            flow_control={},
            legacy_test_suite=suite,
            created_by=suite.created_by,
            created_at=suite.created_at,
        )

        # 2. 迁移步骤 (TestSuiteRequest -> ScenarioStep)
        suite_requests = TestSuiteRequest.objects.filter(test_suite=suite).order_by('order')
        for idx, suite_request in enumerate(suite_requests, start=1):
            self.migrate_request(suite_request, scenario, idx)

        # 3. 迁移评审记录
        review_records = TestSuiteReviewRecord.objects.filter(test_suite=suite)
        for record in review_records:
            self.migrate_review(record, scenario)

        return scenario

    def migrate_request(self, suite_request, scenario, step_number):
        """迁移单个测试套件请求为场景步骤"""
        api_request = suite_request.request

        # 创建 ScenarioStep
        step = ScenarioStep.objects.create(
            scenario=scenario,
            step_type='request',
            step_number=step_number,
            step_alias=f'step_{step_number}',
            name=api_request.name if api_request else f'步骤 {step_number}',
            api_request=api_request,
            override_enabled=suite_request.enabled,
            override_method=api_request.method if api_request else 'GET',
            override_url=api_request.url if api_request else '',
            override_headers=api_request.headers if api_request else {},
            override_params=api_request.params if api_request else {},
            override_body=api_request.body if api_request else {},
            override_assertions=suite_request.assertions or [],
            override_extractors=[],
            pre_script='',
            post_script='',
        )

        return step

    def migrate_review(self, record, scenario):
        """迁移评审记录"""
        ScenarioReviewRecord.objects.create(
            scenario=scenario,
            reviewer=record.reviewer,
            status=record.status,
            comment=record.comment or '',
            reviewed_at=record.reviewed_at,
            created_at=record.created_at,
        )
