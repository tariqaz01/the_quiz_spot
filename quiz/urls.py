from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/subjects/', views.manage_subjects, name='manage_subjects'),
    path('admin/subjects/add/', views.add_subject, name='add_subject'),
    path('admin/subjects/edit/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('admin/subjects/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('admin/questions/', views.manage_questions, name='manage_questions'),
    path('admin/questions/add/', views.add_question, name='add_question'),
    path('admin/questions/edit/<int:question_id>/', views.edit_question, name='edit_question'),
    path('admin/questions/delete/<int:question_id>/', views.delete_question, name='delete_question'),
    path('admin/results/', views.view_results, name='view_results'),
    
    # User URLs
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('select-subject/', views.select_subject, name='select_subject'),
    path('start-quiz/<int:subject_id>/', views.start_quiz, name='start_quiz'),
    path('take-quiz/', views.take_quiz, name='take_quiz'),
    path('submit-quiz/', views.submit_quiz, name='submit_quiz'),
    path('quiz-result/<int:quiz_id>/', views.quiz_result, name='quiz_result'),
    path('quiz-history/', views.quiz_history, name='quiz_history'),
]