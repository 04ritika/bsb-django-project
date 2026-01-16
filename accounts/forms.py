
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

from django import forms
from .models import ImagePost, BlogPost, PollPost, PollOption, Comment
from .models import Post


class ImagePostForm(forms.ModelForm):
    caption = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = ImagePost
        fields = ['image']

class BlogPostForm(forms.ModelForm):
    caption = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = BlogPost
        fields = ['title', 'content']

class PollPostForm(forms.ModelForm):
    caption = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    option1 = forms.CharField(max_length=100, required=True)
    option2 = forms.CharField(max_length=100, required=True)
    option3 = forms.CharField(max_length=100, required=False)
    option4 = forms.CharField(max_length=100, required=False)
    duration_hours = forms.IntegerField(min_value=1, max_value=168, initial=24)
    
    class Meta:
        model = PollPost
        fields = ['question']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2})
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'phone_number', 'birth_date', 'profile_picture', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# Update your forms.py to include Bootstrap classes
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError

class RequestResetForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        
        try:
            user = User.objects.get(username=username, email=email)
            cleaned_data['user'] = user
        except User.DoesNotExist:
            raise ValidationError("No user found with the provided username and email.")
        
        return cleaned_data

class VerifyOTPForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.HiddenInput())
    otp = forms.CharField(
        label='OTP', 
        max_length=6, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP'
        })
    )
    
    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit() or len(otp) != 6:
            raise ValidationError("OTP must be a 6-digit number.")
        return otp

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].help_text = "Your password must contain at least 8 characters."
        self.fields['new_password2'].help_text = "Enter the same password as above, for verification."