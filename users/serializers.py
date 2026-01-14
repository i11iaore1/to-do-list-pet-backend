from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ("pk", "email", "nickname", "password", "created_at", "updated_at")

        read_only_fields = ("pk", "created_at", "updated_at")
        write_only_fields = ("password", )

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            nickname=validated_data.get('nickname', ''),
            password=validated_data['password']
        )
        return user
