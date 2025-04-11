from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar']  # Only required fields for setup

        
class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'avatar',
            'profile_public',
            'username',
            'bio',
            'email',
            'facebook_url',
            'twitter_url',
            'instagram_url',
            'linkedin_url'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Add Bootstrap classes to all fields automatically
    #     for field in self.fields:
    #         if field != 'avatar' and field != 'profile_public':
    #             self.fields[field].widget.attrs.update({'class': 'form-control'})