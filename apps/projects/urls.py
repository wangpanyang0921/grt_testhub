from django.urls import path
from . import views, project_list_views

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list'),
    path('all/', views.get_all_projects, name='all-projects'),
    path('with-menus/', views.get_projects_with_menus, name='projects-with-menus'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/members/', views.get_project_members, name='get-project-members'),
    path('<int:project_id>/members/add/', views.add_project_member, name='add-member'),
    path('<int:project_id>/members/<int:member_id>/', views.remove_project_member, name='remove-member'),
    path('<int:project_id>/environments/', views.ProjectEnvironmentListCreateView.as_view(), name='environment-list'),
    path('list/', project_list_views.user_projects_list, name='user-projects-list'),
    # 端菜单管理
    path('<int:project_id>/menus/', views.get_project_menus, name='get-project-menus'),
    path('<int:project_id>/menus/create/', views.create_project_menu, name='create-project-menu'),
    path('<int:project_id>/menus/<int:menu_id>/update/', views.update_project_menu, name='update-project-menu'),
    path('<int:project_id>/menus/<int:menu_id>/delete/', views.delete_project_menu, name='delete-project-menu'),
]