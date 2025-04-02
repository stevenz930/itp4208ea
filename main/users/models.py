from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/',default='blank_profile.png',blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30,unique=False,blank=False)

    is_instructor = models.BooleanField(default=False)
    profile_public = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.username

    def __str__(self):
        return self.username or self.email

    def get_social_connection(self, platform):
        return self.socialmediaconnection_set.filter(platform=platform).first()


# class SocialMediaConnection(models.Model):
#     SOCIAL_MEDIA_CHOICES = [
#         ('FB','Facebook'),
#         ('IG','Instagram'),
#         ('TW','Twitter'),
#     ]

#     user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
#     platform = models.CharField(max_length=2, choices=SOCIAL_MEDIA_CHOICES)
#     account_id = models.CharField(max_length=100)
#     access_token = models.CharField(max_length=255, blank=True, null=True)
#     data_connected = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'platform')

    