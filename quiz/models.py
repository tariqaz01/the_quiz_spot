from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject.name}: {self.text[:50]}..."

    class Meta:
        ordering = ['subject', 'id']

class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField()
    percentage = models.FloatField(default=0)
    status = models.CharField(
        max_length=10,
        choices=[('Pass', 'Pass'), ('Fail', 'Fail')],
        default='Fail'
    )

    def __str__(self):
        return f"{self.user.username} - {self.subject.name} - {self.date_taken}"

    def save(self, *args, **kwargs):
        if self.total_questions > 0:
            self.percentage = (self.score / self.total_questions) * 100
            self.status = 'Pass' if self.percentage >= 40 else 'Fail'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_taken']

class QuizResponse(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Response for {self.quiz} - Question {self.question.id}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    total_quizzes_taken = models.IntegerField(default=0)
    average_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_stats(self):
        quizzes = self.user.quizzes.all()
        self.total_quizzes_taken = quizzes.count()
        if self.total_quizzes_taken > 0:
            self.average_score = sum(q.percentage for q in quizzes) / self.total_quizzes_taken
        self.save()