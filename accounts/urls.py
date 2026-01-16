from django.urls import path
from . import views
from . import views_club


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
     path('search/', views.search_users, name='search_users'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    path('post/create/<str:post_type>/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('poll/vote/<int:option_id>/', views.vote_poll, name='vote_poll'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('club/create/', views_club.create_club, name='create_club'),
    path('club/<slug:slug>/', views_club.club_profile, name='club_profile'),
    path('club/<slug:slug>/edit/', views_club.edit_club_profile, name='edit_club_profile'),
    path('my-clubs/', views_club.my_clubs, name='my_clubs'),
    path('clubs/', views_club.all_clubs, name='all_clubs'),
    path('club/<slug:slug>/add-member/', views_club.add_club_member, name='add_club_member'),
    # Add to urls.py
path('club/<slug:slug>/create-team/', views_club.create_team, name='create_team'),
path('club/<slug:slug>/team/<int:team_id>/', views_club.team_detail, name='team_detail'),
path('club/<slug:slug>/team/<int:team_id>/add-member/', views_club.add_team_member, name='add_team_member'),
path('club/<slug:slug>/create-event/', views_club.create_event, name='create_event'),
path('club/<slug:slug>/event/<int:event_id>/', views_club.event_detail, name='event_detail'),
path('clubs/<slug:slug>/add-faculty/', views_club.add_faculty_member, name='add_faculty_member'),
path('clubs/<slug:club_slug>/events/<int:event_id>/add-gallery-image/', views_club.add_gallery_image, name='add_gallery_image'),
path('clubs/<slug:club_slug>/events/<int:event_id>/gallery-images/<int:image_id>/delete/', views_club.delete_gallery_image, name='delete_gallery_image'),

      # Password reset URLs
    path('password/forgot/', views.forgot_password, name='forgot_password'),
    path('password/verify-otp/<str:username>/', views.verify_otp, name='verify_otp'),
    path('password/reset/<str:username>/', views.reset_password, name='reset_password'),

    
    
]





from . import views_student

urlpatterns += [
    path('student/register/', views_student.student_register, name='student_register'),
    path('student/profile/', views_student.student_profile, name='student_profile'),
    path('student/<str:username>/', views_student.public_student_profile, name='public_student_profile'),
    path('students/', views_student.all_students, name='all_students'),
]


urlpatterns += [
    
    path('blogs/', views.blog_page, name='blogs'),  # Add this line for the blog page
]

from django.urls import path
from . import views

urlpatterns += [
    # Course URLs
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),

    # Notice URLs
    path('notices/', views.notice_list, name='notice_list'),
]
