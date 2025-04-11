
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        try:
            if email:
                user = User.objects.get(email=email)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None