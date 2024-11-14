from rest_framework import serializers
from authentication.models import User


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'password', 'password_2')

    def validate(self, attrs):
        password = attrs.get('password')
        password_2 = attrs.get('password_2')
        if password != password_2:
            raise serializers.ValidationError('Passwords must match')

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_2')
        user = User.objects.create_user(**validated_data)
        return user
