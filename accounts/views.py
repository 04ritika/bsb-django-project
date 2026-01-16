from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from .forms import UserRegisterForm

from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, ImagePost, BlogPost, PollPost, PollOption, Comment
from .forms import ImagePostForm, BlogPostForm, PollPostForm, CommentForm



from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
def register_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type == 'student':
            return redirect('student_register')
        elif user_type == 'club':
            return redirect('create_club')
        else:
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
        
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'auth/profile.html', context)

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def home_view(request):
    posts = Post.objects.select_related(
        'user', 
        'user__profile', 
        'image_post', 
        'blog_post', 
        'poll_post'
    ).prefetch_related(
        'comments', 
        'likes', 
        'poll_post__options',
        'poll_post__options__votes'
    ).order_by('-created_at').all()
    
    return render(request, 'home.html', {'posts': posts})


# Add these new views
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(username=request.user.username)
    else:
        users = User.objects.exclude(username=request.user.username)[:5]
    
    return render(request, 'auth/search_users.html', {
        'users': users,
        'query': query
    })

@login_required
def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'auth/public_profile.html', {
        'profile_user': user
    })


# accounts/views.py (Add these views)
@login_required
def create_post(request, post_type):
    if request.method == 'POST':
        if post_type == 'image':
            form = ImagePostForm(request.POST, request.FILES)
            if form.is_valid():
                post = Post.objects.create(
                    user=request.user,
                    post_type='image',
                    caption=form.cleaned_data['caption']
                )
                image_post = form.save(commit=False)
                image_post.post = post
                image_post.save()
                messages.success(request, 'Image posted successfully!')
                
        elif post_type == 'blog':
            form = BlogPostForm(request.POST)
            if form.is_valid():
                post = Post.objects.create(
                    user=request.user,
                    post_type='blog',
                    caption=form.cleaned_data['caption']
                )
                blog_post = form.save(commit=False)
                blog_post.post = post
                blog_post.save()
                messages.success(request, 'Blog posted successfully!')
                
        elif post_type == 'poll':
            form = PollPostForm(request.POST)
            if form.is_valid():
                post = Post.objects.create(
                    user=request.user,
                    post_type='poll',
                    caption=form.cleaned_data['caption']
                )
                poll_post = form.save(commit=False)
                poll_post.post = post
                poll_post.ends_at = timezone.now() + timedelta(hours=form.cleaned_data['duration_hours'])
                poll_post.save()
                
                # Create poll options
                options = [form.cleaned_data[f'option{i}'] for i in range(1, 5) if form.cleaned_data.get(f'option{i}')]
                for option_text in options:
                    PollOption.objects.create(poll=poll_post, option_text=option_text)
                    
                messages.success(request, 'Poll created successfully!')
        
        return redirect('home')
    else:
        if post_type == 'image':
            form = ImagePostForm()
        elif post_type == 'blog':
            form = BlogPostForm()
        elif post_type == 'poll':
            form = PollPostForm()
            
    return render(request, 'posts/create_post.html', {
        'form': form,
        'post_type': post_type
    })

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    })

@login_required
@require_POST
def vote_poll(request, option_id):
    option = get_object_or_404(PollOption, id=option_id)
    poll = option.poll
    
    if timezone.now() > poll.ends_at:
        return JsonResponse({'error': 'This poll has ended'}, status=400)
        
    # Remove any existing votes by this user on this poll
    for opt in poll.options.all():
        opt.votes.remove(request.user)
    
    # Add new vote
    option.votes.add(request.user)
    
    # Calculate percentages for all options
    total_votes = sum(opt.votes.count() for opt in poll.options.all())
    results = {
        str(opt.id): {
            'percentage': (opt.votes.count() / total_votes * 100) if total_votes > 0 else 0,
            'votes': opt.votes.count()
        }
        for opt in poll.options.all()
    }
    
    return JsonResponse({'results': results})

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.save()
        return JsonResponse({
            'success': True,
            'comment_html': render_to_string('posts/comment.html', {'comment': comment})
        })
    return JsonResponse({'error': form.errors}, status=400)

# Modify the existing home_view
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    posts = Post.objects.select_related(
        'user', 
        'user__profile', 
        'image_post', 
        'blog_post', 
        'poll_post'
    ).prefetch_related(
        'comments', 
        'likes', 
        'poll_post__options',
        'poll_post__options__votes'
    ).order_by('-created_at')
    
    context = {
        'posts': posts,
        'user': request.user
    }
    return render(request, 'home.html', context)
# Modify the existing profile_view and public_profile view to include posts

@login_required
def profile_view(request):
    posts = Post.objects.select_related(
        'image_post', 
        'blog_post', 
        'poll_post'
    ).prefetch_related(
        'comments', 
        'likes'
    ).filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'posts': posts
    }
    return render(request, 'auth/profile.html', context)

@login_required
def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'user', 
        'image_post', 
        'blog_post', 
        'poll_post'
    ).prefetch_related(
        'comments', 
        'likes', 
        'poll_post__options',
        'poll_post__options__votes'
    ).filter(user=profile_user).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'posts_count': posts.count(),
        'likes_count': sum(post.likes.count() for post in posts),
    }
    return render(request, 'auth/public_profile.html', context)

# accounts/views.py

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()
    
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def blog_detail(request, slug):
    blog_post = get_object_or_404(BlogPost, slug=slug)
    post = blog_post.post
    comments = post.comments.all()
    comment_form = CommentForm()
    
    return render(request, 'posts/blog_detail.html', {
        'post': post,
        'blog_post': blog_post,
        'comments': comments,
        'comment_form': comment_form
    })


from django.shortcuts import render
from .models import BlogPost

def blog_page(request):
    blogs = BlogPost.objects.select_related('post', 'post__user').all().order_by('-post__created_at')
    return render(request, 'posts/blogs.html', {'blogs': blogs})


#courses
from django.shortcuts import render, get_object_or_404
from .models import Course, Category

def course_list(request):
    search_query = request.GET.get('search', '').strip()
    categories = Category.objects.prefetch_related('courses')

    if search_query:
        # Filter categories based on search
        categories = categories.filter(
            courses__title__icontains=search_query
        ).distinct()

        # Filter the courses for each category
        for category in categories:
            category.filtered_courses = category.courses.filter(
                title__icontains=search_query
            )
    else:
        for category in categories:
            category.filtered_courses = category.courses.all()

    return render(request, 'courses/course_list.html', {
        'categories': categories,
        'search_query': search_query
    })

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/course_details.html', {
        'course': course
    })


# notices/views.py
from django.shortcuts import render
from .models import NoticeBoard, Notice  # Updated import

def notice_list(request):
    boards = NoticeBoard.objects.all()  # Changed from categories to boards
    notices_by_board = {}  # Changed from notices_by_category
    
    for board in boards:  # Changed from category to board
        notices_by_board[board] = Notice.objects.filter(
            board=board,  # Changed from category to board
            is_active=True
        ).order_by('-created_at')
    
    context = {
        'notices_by_board': notices_by_board,  # Changed from notices_by_category
    }
    return render(request, 'notices/notice_list.html', context)



# accounts/views.py (add to existing file)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import PasswordResetToken
from .forms import RequestResetForm, VerifyOTPForm, CustomSetPasswordForm

def forgot_password(request):
    if request.method == 'POST':
        form = RequestResetForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            
            # Generate OTP
            otp = PasswordResetToken.generate_otp()
            PasswordResetToken.objects.create(user=user, token=otp)
            
            # Send email with OTP
            subject = 'Password Reset OTP'
            message = f'Your OTP for password reset is: {otp}\nThis OTP is valid for 15 minutes.'
            html_message = render_to_string('auth/reset_email.html', {'otp': otp, 'user': user})
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(request, f'An OTP has been sent to {user.email}')
            return redirect('verify_otp', username=user.username)
    else:
        form = RequestResetForm()
    
    return render(request, 'auth/forgot_password.html', {'form': form})

def verify_otp(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'Invalid username.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        form.fields['username'].initial = username
        
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            # Get the latest unused OTP for this user
            token_obj = PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).order_by('-created_at').first()
            
            if token_obj and token_obj.token == otp and token_obj.is_valid():
                token_obj.is_used = True
                token_obj.save()
                
                # Redirect to set new password
                return redirect('reset_password', username=username)
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
    else:
        form = VerifyOTPForm(initial={'username': username})
    
    return render(request, 'auth/verify_otp.html', {'form': form, 'username': username})

def reset_password(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'Invalid username.')
        return redirect('forgot_password')
    
    # Check if user has verified their OTP
    token_obj = PasswordResetToken.objects.filter(
        user=user,
        is_used=True
    ).order_by('-created_at').first()
    
    if not token_obj:
        messages.error(request, 'Please verify your OTP first.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
            return redirect('login')
    else:
        form = CustomSetPasswordForm(user)
    
    return render(request, 'auth/reset_password.html', {'form': form, 'username': username})


def about_view(request):
    return render(request, 'about.html')
