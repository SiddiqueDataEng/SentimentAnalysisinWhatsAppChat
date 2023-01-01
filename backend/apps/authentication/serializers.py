"""
Serializers for authentication app
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'preferred_language'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    full_name = serializers.ReadOnlyField()
    is_premium = serializers.ReadOnlyField(source='profile.is_premium')
    api_calls_remaining = serializers.ReadOnlyField(source='profile.api_calls_remaining')
    total_chats_analyzed = serializers.ReadOnlyField(source='profile.total_chats_analyzed')
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'avatar', 'bio', 'location', 'birth_date', 'preferred_language',
            'theme_preference', 'is_premium', 'api_calls_remaining',
            'total_chats_analyzed', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'username', 'date_joined', 'last_login')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'avatar', 'bio', 'location',
            'birth_date', 'preferred_language', 'theme_preference'
        )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class UserStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for user statistics
    """
    class Meta:
        model = UserProfile
        fields = (
            'total_chats_analyzed', 'total_messages_processed',
            'favorite_analysis_type', 'subscription_type',
            'api_calls_count', 'api_calls_remaining'
        )
        read_only_fields = fields