# accounts/admin.py
from django.contrib import admin
from .models import Profile, Post, ImagePost, BlogPost, PollPost, PollOption, Comment
from .models import ClubProfile

admin.site.register(ClubProfile)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(ImagePost)
admin.site.register(BlogPost)
admin.site.register(PollPost)
admin.site.register(PollOption)
admin.site.register(Comment)

from .models import ClubMember

admin.site.register(ClubMember)


from django.contrib import admin
from .models import StudentProfile

admin.site.register(StudentProfile)

from .models import Course, CourseContent,Category

class CourseContentInline(admin.StackedInline):
    model = CourseContent
    extra = 1
    fields = ['title', 'content_type', 'text_content', 'file', 'order', 'file_preview']
    readonly_fields = ['file_preview']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at', 'header_preview']
    list_filter = ['created_at', 'category']
    search_fields = ['title', 'description']
    readonly_fields = ['header_preview']
    fields = ['title', 'category', 'description', 'header_image', 'header_preview']
    inlines = [CourseContentInline]

    
@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'content_type', 'order', 'file_preview']
    list_filter = ['course', 'content_type']
    search_fields = ['title', 'course__title']
    readonly_fields = ['file_preview']
    ordering = ['course', 'order']

# notices/admin.py
from django.contrib import admin
from .models import NoticeBoard, Notice  # Updated import

@admin.register(NoticeBoard)  # Changed from Category to NoticeBoard
class NoticeBoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'created_at', 'is_active')  # Changed category to board
    list_filter = ('board', 'is_active', 'created_at')  # Changed category to board
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'


from .models import Team, TeamMember, ClubFAQ, Event, PasswordResetToken

# Register Team and TeamMember
admin.site.register(Team)
admin.site.register(TeamMember)

# Register ClubFAQ
admin.site.register(ClubFAQ)

# Register Event with a custom admin class
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'event_type', 'start_date', 'end_date', 'is_upcoming')
    list_filter = ('event_type', 'is_upcoming', 'club')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'    


    from django.contrib import admin
from .models import FacultyMember, EventGalleryImage

# Register FacultyMember with a custom admin class
@admin.register(FacultyMember)
class FacultyMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'club', 'position', 'department', 'email')
    list_filter = ('club', 'department', 'position')
    search_fields = ('name', 'email', 'bio')

# Register EventGalleryImage with a custom admin class
@admin.register(EventGalleryImage)
class EventGalleryImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption', 'uploaded_at')
    list_filter = ('event', 'uploaded_at')
    search_fields = ('caption', 'description', 'event__title')
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" />')
        return "No image"
    image_preview.short_description = 'Image Preview'

# Register PasswordResetToken
@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token',)