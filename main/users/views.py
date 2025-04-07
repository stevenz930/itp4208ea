
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileSettingsForm
from .backends import EmailOrUsernameModelBackend
from django.contrib.auth.decorators import login_required
from courses.models import Course, CourseCategory
from users.models import CustomUser

def home_view(request):
    courses = Course.objects.filter(is_published=True).distinct()#all course data
    #courses_categories = CourseCategory.objects.values_list('name', flat=True).distinct()
    courses_categories = CourseCategory.objects.distinct()#all courses_categories data
    #print("[courses]:", courses)
    #print("[courses_categories]:", courses_categories)
    instructors = CustomUser.objects.filter(is_instructor=True)

    context = {
        "courses": courses,
        "coursetypes": courses_categories,
        "instructors": instructors,
    }
    return render(request, 'home.html', context)

def custom_login(request):
    if request.method == 'POST':
        # Get email or username from the form
        email_or_username = request.POST.get('email') 
        password = request.POST.get('password')
        
        # First try to authenticate with email
        user = authenticate(request, email=email_or_username, password=password)
        
        # If that fails, try with username
        if user is None:
            user = authenticate(request, username=email_or_username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email/username or password")
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'registration/login.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='users.backends.EmailOrUsernameModelBackend')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required(login_url='login')
def profile(request):
    user = request.user
    return render(request,'profile/profile.html',{'user':user})

# @login_required
# def setup_profile(request):
#     # Check if profile already has basic info
#     if request.user.username and request.user.email:
#         return redirect('profile_settings')
    
#     if request.method == 'POST':
#         form = ProfileSetupForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('profile_settings')
#     else:
#         form = ProfileSetupForm(instance=request.user)
    
#     return render(request, 'setup_profile.html', {'form': form})

@login_required
def profile_settings(request):
    if request.method == 'POST':
        # Explicitly specify data sources
        form = ProfileSettingsForm(
            data=request.POST,  # Explicit POST data
            files=request.FILES,  # Explicit files
            instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_settings')
    else:
        form = ProfileSettingsForm(instance=request.user)
    
    return render(request, 'profile/profile_settings.html', {'form': form})

def instructor_detail(request, instructor_id):
    instructor = CustomUser.objects.filter(is_instructor=True, id=instructor_id)

    context = {
        "instructor": instructor,
    }
    return render(request, 'instructor_detail.html', context)