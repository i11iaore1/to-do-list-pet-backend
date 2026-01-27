from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate


User = get_user_model()


class UserProfileInfoSerializer(serializers.ModelSerializer):
    """
    - As deserializer takes in
      (nickname, password)
      and can only edit an existing account
    - As serializer returns profile info
      (pk, email, nickname, created_at, updated_at)
    """
    class Meta:
        model = User
        fields = ("pk", "email", "password", "nickname", "created_at", "updated_at")

        read_only_fields = ("pk", "email", "created_at", "updated_at")

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class RegisterRequestSerializer(serializers.ModelSerializer):
    """
    ONLY FOR DESEREALIZATION\n
    takes in (email, nickname, password)
    and can only create an account
    """
    class Meta:
        model = User
        fields = ("email", "nickname", "password")

        extra_kwargs = {
            "email": {"write_only": True},
            "nickname": {"write_only": True},
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        # Mandatory because cant use objects.create
        # For password hashing 
        return User.objects.create_user(**validated_data)


class LoginRequestSerializer(serializers.Serializer):
    """
    ONLY FOR DESEREALIZATION\n
    takes in (email, password)
    and can only create an account
    """
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Wrong email or password")

        if not user.is_active:
            raise serializers.ValidationError("User is deactivated")

        attrs["user"] = user

        return attrs
