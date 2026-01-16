from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

class Post(models.Model):
    POST_TYPES = (
        ('image', 'Image Post'),
        ('blog', 'Blog Post'),
        ('poll', 'Poll Post'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=5, choices=POST_TYPES)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    class Meta:
        ordering = ['-created_at']

class ImagePost(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='image_post')
    image = models.ImageField(upload_to='post_images/')

class BlogPost(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='blog_post')
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class PollPost(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='poll_post')
    question = models.CharField(max_length=200)
    ends_at = models.DateTimeField()

class PollOption(models.Model):
    poll = models.ForeignKey(PollPost, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=100)
    votes = models.ManyToManyField(User, related_name='poll_votes', blank=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True,null=True)
    address = models.TextField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)



from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class ClubProfile(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_clubs')
    club_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='club_profile')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)
    club_logo = models.ImageField(upload_to='club_logos/', blank=True)
    established_date = models.DateField()
    website = models.URLField(blank=True)
    email = models.EmailField(unique=True)
    club_type = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name        
    

# Update models.py
class ClubMember(models.Model):
    club = models.ForeignKey(ClubProfile, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_memberships')
    role = models.CharField(max_length=50, default='Member')  # Role in the club
    is_core_team = models.BooleanField(default=False)  # Flag for core team members
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.club.name}"
    

    # Add to models.py
class Team(models.Model):
    club = models.ForeignKey(ClubProfile, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.club.name}"

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    club_member = models.ForeignKey(ClubMember, on_delete=models.CASCADE, related_name='team_memberships')
    team_role = models.CharField(max_length=50, default='Member')  # Specific role in the team
    
    def __str__(self):
        return f"{self.club_member.user.username} - {self.team.name}"
    

# Add to models.py
class ClubFAQ(models.Model):
    club = models.ForeignKey(ClubProfile, on_delete=models.CASCADE, related_name='faqs')
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    asked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asked_questions')
    is_approved = models.BooleanField(default=False)  # To control which questions are visible
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Q: {self.question[:50]}... - {self.club.name}"
    
    class Meta:
        ordering = ['-created_at']    



from django.db import models
from django.contrib.auth.models import User
from .models import ClubProfile

class EventManager(models.Manager):
    def get_upcoming(self):
        """
        Returns upcoming events and updates status of past events.
        """
        current_time = timezone.now()
        # Update events that have ended
        self.filter(end_date__lte=current_time, is_upcoming=True).update(is_upcoming=False)
        # Return upcoming events
        return self.filter(is_upcoming=True)
    
    def get_past(self):
        """
        Returns past events after ensuring statuses are up to date.
        """
        current_time = timezone.now()
        # Update events that have ended
        self.filter(end_date__lte=current_time, is_upcoming=True).update(is_upcoming=False)
        # Return past events
        return self.filter(is_upcoming=False)


class Event(models.Model):
    club = models.ForeignKey(ClubProfile, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=300)
    event_image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    
    # Distinguish between upcoming and past events
    is_upcoming = models.BooleanField(default=True)
    
    # Optional registration link or external link
    registration_link = models.URLField(blank=True, null=True)
    
    # Track who created the event
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Additional event details
    max_participants = models.IntegerField(blank=True, null=True)
    event_type = models.CharField(max_length=100, choices=[
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('conference', 'Conference'),
        ('social', 'Social Event'),
        ('competition', 'Competition'),
        ('other', 'Other')
    ])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EventManager()
    
    def __str__(self):
        return f"{self.title} - {self.club.name}"

    class Meta:
        ordering = ['-start_date']
        
    def save(self, *args, **kwargs):
        # Check if event has already passed when saving
        if self.end_date and self.end_date < timezone.now():
            self.is_upcoming = False
        super().save(*args, **kwargs)


# Add to models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FacultyMember(models.Model):
    club = models.ForeignKey(ClubProfile, on_delete=models.CASCADE, related_name='faculty_members')
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)  # e.g., Faculty Advisor, Mentor
    department = models.CharField(max_length=100, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='faculty_pics/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    added_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} - {self.position} ({self.club.name})"

    
class EventGalleryImage(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='event_gallery/')
    caption = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.event.title} - {self.caption}"
    
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    major = models.CharField(max_length=100)
    year_of_study = models.IntegerField(choices=[
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
        (5, 'Fifth Year'),
    ])
    date_of_birth = models.DateField()
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='student_pics/', blank=True)
    university = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Student Profile"

# accounts/forms_student.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile

class StudentUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class StudentProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'major', 'year_of_study', 'date_of_birth', 
                 'bio', 'profile_picture', 'university', 'department']
        
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError('This student ID is already registered.')
        return student_id
    

#course

    #course
from django.db import models
from django.utils.html import mark_safe

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)  # For controlling category display order

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    header_image = models.ImageField(upload_to='course_headers/',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def header_preview(self):
        if self.header_image:
            return mark_safe(f'<img src="{self.header_image.url}" width="150" />')
        return "No image"
    header_preview.short_description = 'Header Image Preview'

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class CourseContent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=[
        ('PDF', 'PDF Document'),
        ('IMAGE', 'Image'),
        ('TEXT', 'Text Content')
    ])
    text_content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='course_content/', blank=True, null=True)
    order = models.IntegerField(default=0)

    def file_preview(self):
        if self.content_type == 'IMAGE' and self.file:
            return mark_safe(f'<img src="{self.file.url}" width="150" />')
        elif self.content_type == 'PDF' and self.file:
            return mark_safe(f'<a href="{self.file.url}" target="_blank">View PDF</a>')
        return "No preview available"
    file_preview.short_description = 'File Preview'

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['order']

  # notices/models.py
from django.db import models

class NoticeBoard(models.Model):  # Changed from Category to NoticeBoard
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Notice Boards"

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    board = models.ForeignKey(NoticeBoard, on_delete=models.CASCADE, related_name='notices')  # Changed from category to board
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']




from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))
    
    def is_valid(self):
        # OTP valid for 15 minutes
        return (not self.is_used) and (timezone.now() - self.created_at).seconds < 900
    
    def __str__(self):
        return f"Password Reset for {self.user.username}"        