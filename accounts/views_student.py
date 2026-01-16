
# accounts/views_student.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .forms_student import StudentUserCreationForm, StudentProfileForm
from .models import StudentProfile, Post
from django.db.models import Count

def student_register(request):
    if request.method == 'POST':
        user_form = StudentUserCreationForm(request.POST)
        profile_form = StudentProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            login(request, user)
            messages.success(request, 'Student registration successful!')
            return redirect('student_profile')
    else:
        user_form = StudentUserCreationForm()
        profile_form = StudentProfileForm()
    
    return render(request, 'student/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def student_profile(request):
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')

    if request.method == 'POST':
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your student profile has been updated!')
            return redirect('student_profile')
    else:
        profile_form = StudentProfileForm(instance=student_profile)

    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'profile_form': profile_form,
        'student': student_profile,
        'posts': posts,
        'post_count': posts.count(),
        'total_likes': posts.aggregate(total_likes=Count('likes'))['total_likes']
    }
    return render(request, 'student/profile.html', context)

@login_required
def public_student_profile(request, username):
    user = get_object_or_404(User, username=username)
    try:
        student_profile = user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')

    posts = Post.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'student': student_profile,
        'posts': posts,
        'post_count': posts.count(),
        'total_likes': posts.aggregate(total_likes=Count('likes'))['total_likes']
    }
    return render(request, 'student/public_profile.html', context)

@login_required
def all_students(request):
    students = StudentProfile.objects.select_related('user').all()
    return render(request, 'student/all_students.html', {'students': students})