# accounts/forms_club.py (New file)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ClubProfile
from django import forms
from django.contrib.auth.models import User
from .models import ClubMember,ClubFAQ
# Add to forms.py
# Corrected forms.py additions
# forms.py
from django import forms

# Update forms.py
class AddMemberForm(forms.Form):
    username = forms.CharField(max_length=150, help_text="Enter the username of the user to add")
    position = forms.CharField(max_length=50, required=True, 
                              help_text="Enter the member's position (e.g., President, Secretary)")
    is_core_team = forms.BooleanField(required=False, initial=True,
                                     help_text="Check if this member is part of the core team")
# Add to forms.py
class CreateTeamForm(forms.Form):
    name = forms.CharField(max_length=100, help_text="Enter the team name")
    description = forms.CharField(widget=forms.Textarea, required=False, 
                               help_text="Describe the team's purpose")
    


class AddTeamMemberForm(forms.Form):
    member = forms.ModelChoiceField(queryset=None, help_text="Select a club member")
    team_role = forms.CharField(max_length=50, required=False, 
                             help_text="Enter the member's role in this team")
    
    def __init__(self, club, *args, **kwargs):
        super(AddTeamMemberForm, self).__init__(*args, **kwargs)
        self.fields['member'].queryset = ClubMember.objects.filter(club=club)


class ClubUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ClubProfileForm(forms.ModelForm):
    established_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = ClubProfile
        fields = ['name', 'description', 'club_logo', 'established_date', 
                 'website', 'email', 'club_type']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if ClubProfile.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered for a club.')
        return email
    

# Add to forms_club.py
class ClubFAQQuestionForm(forms.ModelForm):
    class Meta:
        model = ClubFAQ
        fields = ['question']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ask your question here...'}),
        }

class ClubFAQAnswerForm(forms.ModelForm):
    class Meta:
        model = ClubFAQ
        fields = ['answer']
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your answer...'}),
        }


from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_date', 'end_date', 
            'location', 'event_image', 'is_upcoming', 
            'registration_link', 'max_participants', 'event_type'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        return cleaned_data        
    


# Add to forms.py
from django import forms
from .models import FacultyMember

class FacultyMemberForm(forms.ModelForm):
    class Meta:
        model = FacultyMember
        fields = ['name', 'position', 'department', 'profile_pic', 'email', 'linkedin', 'website', 'bio']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }    