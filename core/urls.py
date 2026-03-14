from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('experience/', views.experience, name='experience'),
    path('projects/', views.projects, name='projects'),
    path('education/', views.education, name='education'),
    path('resume/', views.resume_view, name='resume'),
    path('contact/', views.contact, name='contact'),
    
    path('account/login/', views.login_view, name='login'),
    path('account/logout/', views.logout_view, name='logout'),
    path('account/forgot-password/', views.forgot_password, name='forgot_password'),
    path('account/verify-code/', views.verify_code, name='verify_code'),
    path('account/reset-password/', views.reset_password, name='reset_password'),
    path('account/dashboard/', views.dashboard, name='dashboard'),
    
    path('account/profile/edit/', views.edit_profile, name='edit_profile'),
    
    path('account/experience/', views.manage_experience, name='manage_experience'),
    path('account/experience/add/', views.add_experience, name='add_experience'),
    path('account/experience/edit/<int:pk>/', views.edit_experience, name='edit_experience'),
    path('account/experience/delete/<int:pk>/', views.delete_experience, name='delete_experience'),
    
    path('account/projects/', views.manage_projects, name='manage_projects'),
    path('account/projects/add/', views.add_project, name='add_project'),
    path('account/projects/edit/<int:pk>/', views.edit_project, name='edit_project'),
    path('account/projects/delete/<int:pk>/', views.delete_project, name='delete_project'),
    
    path('account/education/', views.manage_education, name='manage_education'),
    path('account/education/add/', views.add_education, name='add_education'),
    path('account/education/edit/<int:pk>/', views.edit_education, name='edit_education'),
    path('account/education/delete/<int:pk>/', views.delete_education, name='delete_education'),
    
    path('account/resume/upload/', views.upload_resume, name='upload_resume'),
    path('account/messages/', views.manage_messages, name='manage_messages'),
    path('account/message/read/<int:pk>/', views.mark_message_read, name='mark_message_read'),
    path('account/message/reply/<int:pk>/', views.send_reply, name='send_reply'),
    path('account/message/delete/<int:pk>/', views.delete_message, name='delete_message'),
    path('account/check-email/', views.check_email, name='check_email'),
]