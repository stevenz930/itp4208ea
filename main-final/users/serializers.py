from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'avatar', 'bio',
            'is_instructor', 'profile_public',
            'facebook_url', 'twitter_url', 
            'instagram_url', 'linkedin_url'
        ]
        read_only_fields = ['email']

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password',
            'is_instructor'
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_instructor=validated_data.get('is_instructor', False)
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'avatar', 'bio',
            'profile_public', 'facebook_url',
            'twitter_url', 'instagram_url', 'linkedin_url'
        ]
