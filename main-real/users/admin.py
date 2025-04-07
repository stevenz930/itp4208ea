from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser #  ,SocialMediaConnection
# Register your models here.

class CustomUserAdmin(UserAdmin):
    # Fields to display in the user list
    list_display = ('email', 'username', 'is_instructor', 'is_staff', 'is_active')
    
    # Filter options
    list_filter = ('is_instructor', 'is_staff', 'is_active', 'profile_public')
    
    # Fieldsets for add/edit pages
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('avatar', 'bio')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_instructor', 'profile_public', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    # Default ordering
    ordering = ('email',)
    
    # Search fields
    search_fields = ('email', 'username')

# Register your models
admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(SocialMediaConnection) 