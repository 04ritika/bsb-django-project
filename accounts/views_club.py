# accounts/views_club.py (New file)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .forms_club import ClubUserCreationForm, ClubProfileForm
from .models import ClubProfile, Post
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ClubProfile, ClubMember,FacultyMember
from .forms_club import AddTeamMemberForm
from .forms_club import CreateTeamForm,AddMemberForm,ClubFAQAnswerForm,ClubFAQQuestionForm,EventForm,FacultyMemberForm
from .models import ClubProfile, ClubMember, Team, TeamMember,ClubFAQ,Event,EventManager,EventGalleryImage
from django.utils import timezone

@login_required
def create_club(request):
    if request.method == 'POST':
        user_form = ClubUserCreationForm(request.POST)
        profile_form = ClubProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            club_user = user_form.save()
            club_profile = profile_form.save(commit=False)
            club_profile.created_by = request.user
            club_profile.club_user = club_user
            club_profile.save()
            
            messages.success(request, 'Club profile created successfully!')
            return redirect('club_profile', slug=club_profile.slug)
    else:
        user_form = ClubUserCreationForm()
        profile_form = ClubProfileForm()
    
    return render(request, 'club/create_club.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def club_profile(request, slug):
    club = get_object_or_404(ClubProfile, slug=slug)
    posts = Post.objects.filter(user=club.club_user).order_by('-created_at')
    
    upcoming_events = Event.objects.get_upcoming().filter(club=club)
    past_events = Event.objects.get_past().filter(club=club)

    # Check if user is a club member or creator
    is_member = ClubMember.objects.filter(club=club, user=request.user).exists()
    is_creator = (request.user == club.created_by)
    can_answer = is_member or is_creator
    
    # Get approved FAQs or all FAQs if user is creator/member
    if can_answer:
        faqs = ClubFAQ.objects.filter(club=club)
    else:
        faqs = ClubFAQ.objects.filter(club=club, is_approved=True)
    
    # Handle question form submission - allow any logged-in user to ask
    if request.method == 'POST' and 'question_submit' in request.POST:
        question_form = ClubFAQQuestionForm(request.POST)
        if question_form.is_valid():
            faq = question_form.save(commit=False)
            faq.club = club
            faq.asked_by = request.user
            # Auto-approve if submitted by creator or member
            if can_answer:
                faq.is_approved = True
            faq.save()
            messages.success(request, 'Your question has been submitted! It will be visible once approved by the club administrator.')
            return redirect('club_profile', slug=slug)
    else:
        question_form = ClubFAQQuestionForm()
    
    # Rest of the view remains the same...
    # Handle answer form submission
    if request.method == 'POST' and 'answer_submit' in request.POST:
        if not can_answer:
            messages.error(request, 'Only club members can answer questions.')
            return redirect('club_profile', slug=slug)
        
        faq_id = request.POST.get('faq_id')
        faq = get_object_or_404(ClubFAQ, id=faq_id, club=club)
        
        answer = request.POST.get('answer')
        if answer:
            faq.answer = answer
            faq.answered_at = timezone.now()
            faq.is_approved = True  # Auto-approve when answered
            faq.save()
            messages.success(request, 'Answer posted successfully!')
        
        return redirect('club_profile', slug=slug)
    
    # Handle FAQ approval/deletion
    if request.method == 'POST' and request.user == club.created_by:
        if 'approve_faq' in request.POST:
            faq_id = request.POST.get('faq_id')
            faq = get_object_or_404(ClubFAQ, id=faq_id, club=club)
            faq.is_approved = True
            faq.save()
            messages.success(request, 'Question approved.')
            return redirect('club_profile', slug=slug)
            
        elif 'delete_faq' in request.POST:
            faq_id = request.POST.get('faq_id')
            faq = get_object_or_404(ClubFAQ, id=faq_id, club=club)
            faq.delete()
            messages.success(request, 'Question deleted.')
            return redirect('club_profile', slug=slug)
    
    context = {
        'club': club,
        'posts': posts,
        'post_count': posts.count(),
        'total_likes': posts.aggregate(total_likes=Count('likes'))['total_likes'],
        'faqs': faqs,
        'question_form': question_form,
        'is_member': is_member,
        'is_creator': is_creator,
        'can_answer': can_answer,
         'upcoming_events': upcoming_events,
        'past_events': past_events
    }
    return render(request, 'club/club_profile.html', context)
@login_required
def edit_club_profile(request, slug):
    club = get_object_or_404(ClubProfile, slug=slug)
    
    if request.user != club.created_by:
        messages.error(request, 'You do not have permission to edit this club profile.')
        return redirect('club_profile', slug=slug)
    
    if request.method == 'POST':
        form = ClubProfileForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            messages.success(request, 'Club profile updated successfully!')
            return redirect('club_profile', slug=club.slug)
    else:
        form = ClubProfileForm(instance=club)
    
    return render(request, 'club/edit_club_profile.html', {'form': form})

@login_required
def my_clubs(request):
    created_clubs = ClubProfile.objects.filter(created_by=request.user)
    return render(request, 'club/my_clubs.html', {'clubs': created_clubs})

@login_required
def all_clubs(request):
    clubs = ClubProfile.objects.all().order_by('-created_at')
    return render(request, 'club/all_clubs.html', {'clubs': clubs})
@login_required
def add_club_member(request, slug):
    club = get_object_or_404(ClubProfile, slug=slug)
    
    if request.user != club.created_by:
        messages.error(request, "You do not have permission to add members to this club.")
        return redirect('club_profile', slug=slug)
    
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            position = form.cleaned_data['position']
            is_core_team = form.cleaned_data['is_core_team']
            
            try:
                user = User.objects.get(username=username)
                
                # Check if the user is already a member
                if ClubMember.objects.filter(club=club, user=user).exists():
                    messages.error(request, f"{username} is already a member of this club.")
                else:
                    ClubMember.objects.create(
                        club=club, 
                        user=user, 
                        role=position,
                        is_core_team=is_core_team
                    )
                    messages.success(request, f"{username} has been added to the club as {position}.")
                return redirect('club_profile', slug=slug)
            except User.DoesNotExist:
                messages.error(request, f"User with username '{username}' does not exist.")
        
    else:
        form = AddMemberForm()

    return render(request, 'club/add_member.html', {'form': form, 'club': club})


# Add to views_club.py
@login_required
def create_team(request, slug):
    club = get_object_or_404(ClubProfile, slug=slug)
    
    if request.user != club.created_by:
        messages.error(request, "You do not have permission to create teams in this club.")
        return redirect('club_profile', slug=slug)
    
    if request.method == 'POST':
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            
            team = Team.objects.create(club=club, name=name, description=description)
            messages.success(request, f"Team '{name}' has been created.")
            return redirect('team_detail', slug=slug, team_id=team.id)
    else:
        form = CreateTeamForm()
    
    return render(request, 'club/create_team.html', {'form': form, 'club': club})

@login_required
def team_detail(request, slug, team_id):
    club = get_object_or_404(ClubProfile, slug=slug)
    team = get_object_or_404(Team, id=team_id, club=club)
    team_members = TeamMember.objects.filter(team=team)
    
    # Get all club members who aren't in this team
    existing_member_ids = team_members.values_list('club_member_id', flat=True)
    available_members = ClubMember.objects.filter(club=club).exclude(id__in=existing_member_ids)
    
    return render(request, 'club/team_detail.html', {
        'club': club,
        'team': team,
        'team_members': team_members,
        'available_members': available_members
    })

@login_required
def add_team_member(request, slug, team_id):
    club = get_object_or_404(ClubProfile, slug=slug)
    team = get_object_or_404(Team, id=team_id, club=club)
    
    if request.user != club.created_by:
        messages.error(request, "You do not have permission to add members to this team.")
        return redirect('team_detail', slug=slug, team_id=team.id)
    
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        team_role = request.POST.get('team_role', '')
        
        if member_id:
            club_member = get_object_or_404(ClubMember, id=member_id, club=club)
            
            # Check if already in team
            if TeamMember.objects.filter(team=team, club_member=club_member).exists():
                messages.error(request, f"{club_member.user.username} is already in this team.")
            else:
                TeamMember.objects.create(team=team, club_member=club_member, team_role=team_role)
                messages.success(request, f"{club_member.user.username} added to the team as {team_role if team_role else 'a member'}.")
        else:
            messages.error(request, "Please select a member to add.")
            
        return redirect('team_detail', slug=slug, team_id=team.id)
    
    # This view now handles form submission directly from the team detail page
    return redirect('team_detail', slug=slug, team_id=team.id)


@login_required
def create_event(request, slug):
    club = get_object_or_404(ClubProfile, slug=slug)
    
    if request.user != club.created_by:
        messages.error(request, "You do not have permission to create events for this club.")
        return redirect('club_profile', slug=slug)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            event.created_by = request.user
            event.save()
            
            messages.success(request, f"Event '{event.title}' has been created successfully.")
            return redirect('club_profile', slug=slug)
    else:
        form = EventForm()
    
    return render(request, 'club/create_event.html', {
        'form': form, 
        'club': club
    })

@login_required
def event_detail(request, slug, event_id):
    club = get_object_or_404(ClubProfile, slug=slug)
    event = get_object_or_404(Event, id=event_id, club=club)
    
    # Update status if needed
    if event.end_date < timezone.now() and event.is_upcoming:
        event.is_upcoming = False
        event.save()
    
    return render(request, 'club/event_detail.html', {
        'club': club,
        'event': event
    })



@login_required
def add_faculty_member(request, slug):
    club = get_object_or_404(ClubProfile, slug=slug)
    
    # Check if user is club creator
    if request.user != club.created_by:
        messages.error(request, "You don't have permission to add faculty members.")
        return redirect('club_profile', slug=slug)
    
    if request.method == 'POST':
        form = FacultyMemberForm(request.POST, request.FILES)
        if form.is_valid():
            faculty_member = form.save(commit=False)
            faculty_member.club = club
            faculty_member.save()
            messages.success(request, 'Faculty member added successfully!')
            return redirect('club_profile', slug=slug)
    else:
        form = FacultyMemberForm()
    
    context = {
        'form': form,
        'club': club,
        'title': 'Add Faculty Member'
    }
    return render(request, 'club/add_faculty_member.html', context)


@login_required
def add_gallery_image(request, club_slug, event_id):
    club = get_object_or_404(ClubProfile, slug=club_slug)  # Changed Club to ClubProfile
    event = get_object_or_404(Event, id=event_id, club=club)
    
    # Check if the user is the club creator
    if request.user != club.created_by:
        messages.error(request, "You don't have permission to add gallery images.")
        return redirect('club_profile', slug=club_slug)  # Also update this parameter name
    
    # Check if the gallery already has 5 images
    if event.gallery_images.count() >= 5:
        messages.error(request, "This event already has the maximum of 5 gallery images.")
        return redirect('club_profile', slug=club_slug)  # Update parameter name
    
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption')
        description = request.POST.get('description')
        
        if not image or not caption:
            messages.error(request, "Image and caption are required.")
            return redirect('club_profile', slug=club_slug)  # Update parameter name
        
        # Create the gallery image
        EventGalleryImage.objects.create(
            event=event,
            image=image,
            caption=caption,
            description=description
        )
        
        messages.success(request, "Gallery image added successfully.")
    
    return redirect('club_profile', slug=club_slug)  # Update parameter name

@login_required
def delete_gallery_image(request, club_slug, event_id, image_id):
    club = get_object_or_404(ClubProfile, slug=club_slug)  # Changed Club to ClubProfile
    event = get_object_or_404(Event, id=event_id, club=club)
    gallery_image = get_object_or_404(EventGalleryImage, id=image_id, event=event)
    
    # Check if the user is the club creator
    if request.user != club.created_by:
        messages.error(request, "You don't have permission to delete gallery images.")
        return redirect('club_profile', slug=club_slug)  # Update parameter name
    
    if request.method == 'POST':
        # Delete the image file
        if gallery_image.image:
            if os.path.isfile(gallery_image.image.path):
                os.remove(gallery_image.image.path)
        
        # Delete the database record
        gallery_image.delete()
        messages.success(request, "Gallery image deleted successfully.")
    
    return redirect('club_profile', slug=club_slug)  # Update parameter name