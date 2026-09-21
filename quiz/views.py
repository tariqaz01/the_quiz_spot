from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Avg
from django.http import JsonResponse
import random
from .models import Subject, Question, Quiz, QuizResponse, UserProfile
from .forms import UserRegistrationForm, SubjectForm, QuestionForm, QuizSettingsForm
from .decorators import admin_required, user_required

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('user_dashboard')

# Admin Views
@admin_required
def admin_dashboard(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_subjects = Subject.objects.count()
    total_questions = Question.objects.count()
    total_quizzes = Quiz.objects.count()
    
    recent_quizzes = Quiz.objects.select_related('user', 'subject').order_by('-date_taken')[:10]
    
    context = {
        'total_users': total_users,
        'total_subjects': total_subjects,
        'total_questions': total_questions,
        'total_quizzes': total_quizzes,
        'recent_quizzes': recent_quizzes,
    }
    return render(request, 'admin/admin_dashboard.html', context)
def custom_404(request, exception):
    return render(request, '404.html', status=404)

@admin_required
def manage_subjects(request):
    subjects = Subject.objects.all().annotate(
        question_count=Count('questions')
    )
    return render(request, 'admin/manage_subjects.html', {'subjects': subjects})

@admin_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('manage_subjects')
    else:
        form = SubjectForm()
    return render(request, 'admin/add_subject.html', {'form': form})

@admin_required
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('manage_subjects')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'admin/edit_subject.html', {'form': form, 'subject': subject})

@admin_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')
    return redirect('manage_subjects')

@admin_required
def manage_questions(request):
    subject_id = request.GET.get('subject')
    if subject_id:
        questions = Question.objects.filter(subject_id=subject_id).select_related('subject')
    else:
        questions = Question.objects.all().select_related('subject')
    subjects = Subject.objects.all()
    return render(request, 'admin/manage_questions.html', {
        'questions': questions,
        'subjects': subjects,
        'selected_subject': subject_id
    })

@admin_required
def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added successfully!')
            return redirect('manage_questions')
    else:
        form = QuestionForm()
    return render(request, 'admin/add_question.html', {'form': form})

@admin_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('manage_questions')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'admin/edit_question.html', {'form': form, 'question': question})

@admin_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
    return redirect('manage_questions')

@admin_required
def view_results(request):
    quizzes = Quiz.objects.select_related('user', 'subject').order_by('-date_taken')
    
    # Filter by subject
    subject_id = request.GET.get('subject')
    if subject_id:
        quizzes = quizzes.filter(subject_id=subject_id)
    
    # Filter by date
    date_filter = request.GET.get('date')
    if date_filter:
        from django.utils import timezone
        from datetime import timedelta
        
        if date_filter == 'today':
            quizzes = quizzes.filter(date_taken__date=timezone.now().date())
        elif date_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            quizzes = quizzes.filter(date_taken__gte=week_ago)
        elif date_filter == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            quizzes = quizzes.filter(date_taken__gte=month_ago)
    
    subjects = Subject.objects.all()
    return render(request, 'admin/view_results.html', {
        'quizzes': quizzes,
        'subjects': subjects
    })

# User Views
@user_required
def user_dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.update_stats()
    
    recent_quizzes = Quiz.objects.filter(user=request.user).select_related('subject').order_by('-date_taken')[:5]
    subjects = Subject.objects.all()
    
    context = {
        'user_profile': user_profile,
        'recent_quizzes': recent_quizzes,
        'subjects': subjects,
        'total_subjects': subjects.count(),
    }
    return render(request, 'user/user_dashboard.html', context)

@user_required
def select_subject(request):
    subjects = Subject.objects.all()
    return render(request, 'user/select_subject.html', {'subjects': subjects})

@user_required
def start_quiz(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = QuizSettingsForm(request.POST)
        if form.is_valid():
            num_questions = form.cleaned_data['num_questions']
            
            # Get random questions from the subject
            questions = list(Question.objects.filter(subject=subject))
            if len(questions) < num_questions:
                messages.error(request, f'Not enough questions available. Only {len(questions)} questions found.')
                return redirect('select_subject')
            
            selected_questions = random.sample(questions, num_questions)
            
            # Store question IDs in session
            request.session['quiz_questions'] = [q.id for q in selected_questions]
            request.session['quiz_subject_id'] = subject_id
            request.session['quiz_current_index'] = 0
            request.session['quiz_answers'] = {}
            
            return redirect('take_quiz')
    else:
        form = QuizSettingsForm()
    
    return render(request, 'user/start_quiz.html', {
        'subject': subject,
        'form': form,
        'total_questions': Question.objects.filter(subject=subject).count()
    })

@user_required
def take_quiz(request):
    if 'quiz_questions' not in request.session:
        return redirect('select_subject')
    
    question_ids = request.session['quiz_questions']
    current_index = request.session['quiz_current_index']
    answers = request.session.get('quiz_answers', {})
    
    if current_index >= len(question_ids):
        return redirect('submit_quiz')
    
    question = get_object_or_404(Question, id=question_ids[current_index])
    
    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        if selected_answer:
            answers[str(question_ids[current_index])] = selected_answer
            request.session['quiz_answers'] = answers
            
            # Move to next question
            if current_index + 1 < len(question_ids):
                request.session['quiz_current_index'] = current_index + 1
                return redirect('take_quiz')
            else:
                return redirect('submit_quiz')
    
    # Get previously selected answer if any
    selected = answers.get(str(question.id), '')
    
    # Calculate progress
    progress = ((current_index + 1) / len(question_ids)) * 100
    
    context = {
        'question': question,
        'current_index': current_index + 1,
        'total_questions': len(question_ids),
        'selected': selected,
        'progress': progress,
    }
    return render(request, 'user/take_quiz.html', context)

@user_required
def submit_quiz(request):
    if 'quiz_questions' not in request.session or 'quiz_subject_id' not in request.session:
        return redirect('select_subject')
    
    question_ids = request.session['quiz_questions']
    subject_id = request.session['quiz_subject_id']
    answers = request.session.get('quiz_answers', {})
    
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Create quiz record
    quiz = Quiz.objects.create(
        user=request.user,
        subject=subject,
        total_questions=len(question_ids)
    )
    
    score = 0
    responses = []
    
    for q_id in question_ids:
        question = get_object_or_404(Question, id=q_id)
        selected = answers.get(str(q_id), '')
        is_correct = (selected == question.correct_answer)
        
        if is_correct:
            score += 1
        
        responses.append(QuizResponse(
            quiz=quiz,
            question=question,
            selected_answer=selected,
            is_correct=is_correct
        ))
    
    # Bulk create responses
    QuizResponse.objects.bulk_create(responses)
    
    # Update quiz score
    quiz.score = score
    quiz.save()
    
    # Update user profile
    profile = UserProfile.objects.get(user=request.user)
    profile.update_stats()
    
    # Clear session data
    del request.session['quiz_questions']
    del request.session['quiz_subject_id']
    del request.session['quiz_current_index']
    del request.session['quiz_answers']
    
    return redirect('quiz_result', quiz_id=quiz.id)

@user_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz.objects.select_related('subject'), id=quiz_id, user=request.user)
    responses = QuizResponse.objects.filter(quiz=quiz).select_related('question')
    
    # Group questions by correctness for analysis
    correct_questions = responses.filter(is_correct=True)
    incorrect_questions = responses.filter(is_correct=False)
    
    context = {
        'quiz': quiz,
        'responses': responses,
        'correct_count': correct_questions.count(),
        'incorrect_count': incorrect_questions.count(),
        'correct_questions': correct_questions,
        'incorrect_questions': incorrect_questions,
    }
    return render(request, 'user/quiz_result.html', context)

@user_required
def quiz_history(request):
    quizzes = Quiz.objects.filter(user=request.user).select_related('subject').order_by('-date_taken')
    
    # Statistics
    total_quizzes = quizzes.count()
    if total_quizzes > 0:
        avg_score = quizzes.aggregate(Avg('percentage'))['percentage__avg']
        pass_count = quizzes.filter(status='Pass').count()
        pass_percentage = (pass_count / total_quizzes) * 100
    else:
        avg_score = 0
        pass_percentage = 0
    
    context = {
        'quizzes': quizzes,
        'total_quizzes': total_quizzes,
        'avg_score': round(avg_score, 2),
        'pass_percentage': round(pass_percentage, 2),
    }
    return render(request, 'user/quiz_history.html', context)