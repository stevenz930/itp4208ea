# courses/urls.py
from django.urls import path
from . import views
# from .views import courses

urlpatterns = [
    path('course_list/', views.course_list, name='course_list'),
]