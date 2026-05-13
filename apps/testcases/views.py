from rest_framework import generics, permissions, status, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import models
import datetime
from .models import TestCase, TestCaseStep, TestCaseAttachment, TestCaseComment
from .serializers import (
    TestCaseSerializer, TestCaseListSerializer, TestCaseCreateSerializer, TestCaseUpdateSerializer
)
from apps.projects.models import Project

class TestCasePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TestCaseListCreateView(generics.ListCreateAPIView):
    queryset = TestCase.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TestCasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'test_type', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TestCaseCreateSerializer
        return TestCaseListSerializer
    
    def get_queryset(self):
        user = self.request.user
        accessible_projects = Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()
        
        queryset = TestCase.objects.filter(
            models.Q(project__in=accessible_projects) | models.Q(project__isnull=True)
        ).select_related(
            'author', 'assignee', 'project'
        ).prefetch_related(
            'versions'
        ).distinct()
        
        # 支持按菜单ID筛选
        menu_id = self.request.query_params.get('menu')
        if menu_id:
            from apps.projects.models import ProjectMenu
            # 获取指定菜单及其所有子菜单的ID
            menu_ids = [int(menu_id)]
            def get_child_menu_ids(parent_id):
                children = ProjectMenu.objects.filter(parent_id=parent_id)
                for child in children:
                    menu_ids.append(child.id)
                    get_child_menu_ids(child.id)
            get_child_menu_ids(int(menu_id))
            queryset = queryset.filter(menu_id__in=menu_ids)
        
        return queryset

    def get_user_accessible_projects(self, user):
        """获取用户有权限访问的项目"""
        return Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        
        # 如果请求中指定了作者（通过author_name），则让序列化器处理作者
        # 否则使用当前登录用户作为作者
        # 端和菜单由序列化器根据 category_path 自动创建
        if self.request.data.get('author_name'):
            # 传递当前用户给序列化器，以便在找不到 author_name 对应用户时使用
            serializer.save(request_user=user)
        else:
            serializer.save(author=user)

class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TestCaseUpdateSerializer
        return TestCaseSerializer
    
    def get_queryset(self):
        user = self.request.user
        accessible_projects = Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()
        # 查询用户有权限访问的项目下的用例，以及 project 为 null 的用例（被删除项目的用例）
        return TestCase.objects.filter(
            models.Q(project__in=accessible_projects) | models.Q(project__isnull=True)
        ).select_related(
            'author', 'assignee', 'project'
        ).prefetch_related(
            'versions', 'step_details', 'attachments', 'comments'
        ).distinct()

    def get_user_accessible_projects(self, user):
        """获取用户有权限访问的项目"""
        return Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()
    
    def perform_update(self, serializer):
        user = self.request.user
        project_id = self.request.data.get('project_id')
        
        if project_id:
            # 检查指定的项目是否存在且用户有权限
            accessible_projects = self.get_user_accessible_projects(user)
            try:
                project = accessible_projects.get(id=project_id)
                serializer.save(project=project)
            except Project.DoesNotExist:
                # 如果指定项目不存在或无权限，保持原项目不变
                serializer.save()
        else:
            # 没有指定项目，保持原项目不变
            serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def testcase_modules(request):
    """获取所有测试用例的模块列表（去重）"""
    user = request.user
    accessible_projects = Project.objects.filter(
        models.Q(owner=user) | models.Q(members=user)
    ).distinct()
    
    # 获取用户有权限访问的所有用例的模块字段
    modules = TestCase.objects.filter(
        project__in=accessible_projects
    ).exclude(
        module__isnull=True
    ).exclude(
        module=''
    ).values_list(
        'module', flat=True
    ).distinct().order_by('module')
    
    return Response(list(modules))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def testcase_statistics(request):
    """获取主线用例统计数据"""
    user = request.user
    accessible_projects = Project.objects.filter(
        models.Q(owner=user) | models.Q(members=user)
    ).distinct()
    
    # 获取用户有权限访问的用例
    queryset = TestCase.objects.filter(
        models.Q(project__in=accessible_projects) | models.Q(project__isnull=True)
    ).select_related('author', 'project')
    
    # 按项目统计
    project_stats = []
    for project in accessible_projects:
        project_cases = queryset.filter(project=project)
        project_stats.append({
            'project_id': project.id,
            'project_name': project.name,
            'total': project_cases.count(),
            'draft': project_cases.filter(status='draft').count(),
            'active': project_cases.filter(status='active').count(),
            'deprecated': project_cases.filter(status='deprecated').count(),
            'high_priority': project_cases.filter(priority='high').count() + project_cases.filter(priority='critical').count(),
        })
    
    # 按状态统计
    status_stats = {
        'draft': queryset.filter(status='draft').count(),
        'active': queryset.filter(status='active').count(),
        'deprecated': queryset.filter(status='deprecated').count(),
    }
    
    # 按优先级统计
    priority_stats = {
        'critical': queryset.filter(priority='critical').count(),
        'high': queryset.filter(priority='high').count(),
        'medium': queryset.filter(priority='medium').count(),
        'low': queryset.filter(priority='low').count(),
    }
    
    # 按作者统计（包含优先级细分和积分）
    author_stats = []
    from django.db.models import Count
    authors = queryset.values('author__username').annotate(count=Count('id')).order_by('-count')[:10]
    for author in authors:
        username = author['author__username']
        author_cases = queryset.filter(author__username=username)
        critical = author_cases.filter(priority='critical').count()
        high = author_cases.filter(priority='high').count()
        medium = author_cases.filter(priority='medium').count()
        low = author_cases.filter(priority='low').count()
        # 积分规则：5个P0/P1 +1分，10个P2/P3 +1分
        score = (critical + high) // 5 + (medium + low) // 10
        author_stats.append({
            'username': username,
            'count': author['count'],
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low,
            'score': score,
        })
    
    # 按月份统计（近6个月）
    from django.utils import timezone
    from datetime import timedelta
    monthly_stats = []
    
    # 获取活跃作者列表（按贡献量排序取前8个）
    top_authors = [a['username'] for a in author_stats[:8]] if author_stats else []
    
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30 * i)
        month_start = month_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            month_end = timezone.now()
        else:
            month_end = month_start + timedelta(days=30)
        
        month_cases = queryset.filter(created_at__gte=month_start, created_at__lt=month_end)
        
        # 按作者统计该月新增用例（按优先级细分）
        author_detail_counts = {}
        for author in top_authors:
            author_cases = month_cases.filter(author__username=author)
            author_detail_counts[author] = {
                'critical': author_cases.filter(priority='critical').count(),
                'high': author_cases.filter(priority='high').count(),
                'medium': author_cases.filter(priority='medium').count(),
                'low': author_cases.filter(priority='low').count(),
                'total': author_cases.count(),
            }
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'count': month_cases.count(),
            'active': month_cases.filter(status='active').count(),
            'author_detail_counts': author_detail_counts,
        })
    monthly_stats.reverse()
    
    return Response({
        'total': queryset.count(),
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'project_stats': project_stats,
        'author_stats': author_stats,
        'monthly_stats': monthly_stats,
        'top_authors': top_authors,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def author_test_cases(request):
    """获取指定作者的用例列表"""
    username = request.GET.get('username')
    priority = request.GET.get('priority', '')
    month = request.GET.get('month', '')
    
    if not username:
        return Response({'error': 'username参数必填'}, status=400)
    
    user = request.user
    accessible_projects = Project.objects.filter(
        models.Q(owner=user) | models.Q(members=user)
    ).distinct()
    
    queryset = TestCase.objects.filter(
        models.Q(project__in=accessible_projects) | models.Q(project__isnull=True),
        author__username=username
    ).select_related('author', 'project')
    
    # 按月份筛选
    if month:
        try:
            year, mon = month.split('-')
            from datetime import date
            import calendar
            month_start = date(int(year), int(mon), 1)
            if int(mon) == 12:
                month_end = date(int(year) + 1, 1, 1)
            else:
                month_end = date(int(year), int(mon) + 1, 1)
            queryset = queryset.filter(
                created_at__gte=datetime.datetime.combine(month_start, datetime.time.min),
                created_at__lt=datetime.datetime.combine(month_end, datetime.time.min)
            )
        except (ValueError, IndexError):
            pass
    
    # 按优先级筛选
    if priority:
        queryset = queryset.filter(priority=priority)
    
    queryset = queryset.order_by('-created_at')
    
    cases = []
    for case in queryset[:200]:  # 限制返回200条
        # 获取归属目录（菜单路径）
        directory = ''
        if case.menu:
            directory = case.menu.name
            # 如果有父级菜单，拼接完整路径
            parent = case.menu.parent
            while parent:
                directory = f"{parent.name} / {directory}"
                parent = parent.parent
        
        cases.append({
            'id': case.id,
            'title': case.title,
            'priority': case.priority,
            'status': case.status,
            'directory': directory or '未分配',
            'menu_id': case.menu_id,
            'created_at': case.created_at.strftime('%Y-%m-%d %H:%M') if case.created_at else None,
        })
    
    # 按目录分组
    grouped = {}
    for case in cases:
        dir_name = case['directory']
        if dir_name not in grouped:
            grouped[dir_name] = []
        grouped[dir_name].append(case)
    
    # 转换为前端需要的树形结构
    grouped_list = [
        {
            'directory': dir_name,
            'count': len(items),
            'cases': items
        }
        for dir_name, items in grouped.items()
    ]
    # 按用例数量降序排列
    grouped_list.sort(key=lambda x: x['count'], reverse=True)
    
    return Response({
        'total': queryset.count(),
        'grouped': grouped_list,
        'cases': cases  # 保留平铺数据备用
    })
