from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Subject, Question, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    registration_number = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'registration_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                registration_number=self.cleaned_data['registration_number']
            )
        return user

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 2}),
        }

class QuizSettingsForm(forms.Form):
    num_questions = forms.IntegerField(
        # requirement changed: allow as few as 5 questions
        min_value=5,
        max_value=100,
        initial=5,
        label="Number of Questions"
    )