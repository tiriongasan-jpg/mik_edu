from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('student-journal/', views.student_journal, name='student_journal'),
    path('lectures/', views.lectures_list, name='lectures_list'),
    path('lecture/<int:pk>/', views.lecture_detail, name='lecture_detail'),
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    
    # Admin panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-groups/', views.admin_groups, name='admin_groups'),
    path('admin-group/<int:group_id>/', views.admin_group_detail, name='admin_group_detail'),
    path('admin-subject/<int:subject_id>/', views.admin_subject_detail, name='admin_subject_detail'),
    path('admin-module/<int:module_id>/', views.admin_module_detail, name='admin_module_detail'),
    path('admin-test/<int:test_id>/', views.admin_test_detail, name='admin_test_detail'),
    path('admin-journal/', views.admin_journal, name='admin_journal'),
    path('admin-journal-group/<int:group_id>/', views.admin_journal_group_detail, name='admin_journal_group_detail'),
    path('admin-journal-subject/<int:subject_id>/', views.admin_journal_subject_detail, name='admin_journal_subject_detail'),
    path('admin-schedule/', views.admin_schedule, name='admin_schedule'),
    path('admin-schedule-group/<int:group_id>/', views.admin_schedule_group, name='admin_schedule_group'),
]

