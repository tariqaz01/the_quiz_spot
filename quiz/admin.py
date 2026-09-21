from django.contrib import admin
from .models import Subject, Question, Quiz, QuizResponse, UserProfile

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'text', 'correct_answer', 'created_at']
    list_filter = ['subject', 'correct_answer']
    search_fields = ['text']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'score', 'total_questions', 'percentage', 'status', 'date_taken']
    list_filter = ['status', 'subject', 'date_taken']
    search_fields = ['user__username']

@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question', 'selected_answer', 'is_correct']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'registration_number', 'total_quizzes_taken', 'average_score']