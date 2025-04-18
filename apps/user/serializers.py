from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from apps.user.models import User, UserType
from apps.user.constants import ADMIN_ROLE_NAME

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Only Admin can access the API as per module and will check if the user is active
        if (
            not self.user.is_active or
            not hasattr(self.user, 'user_type') or
            self.user.user_type.name != ADMIN_ROLE_NAME
        ):
            raise AuthenticationFailed('You are not authorized to access the API.', code='authorization')
  
        data['email'] = self.user.email
        data['user_type'] = self.user.user_type.name
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name

        return data

class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.StringRelatedField(read_only=True)
    user_type_id = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.all(),
        source='user_type',
        write_only=True
    )
    password = serializers.CharField(write_only=True, required=True)
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'is_active',
            'is_staff',
            'is_superuser',
            'user_type',
            'user_type_id'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']