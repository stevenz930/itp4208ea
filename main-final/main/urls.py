"""
URL configuration for learning_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views 
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static # Make sure this import works

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.custom_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('admin/',admin.site.urls),
    path('users/', include('users.urls')),
    path('courses/', include('courses.urls')),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('faq/', views.faq, name='faq'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)