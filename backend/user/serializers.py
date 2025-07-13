from rest_framework import serializers
from .models import UserAccount

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # 🔓 Direct plain text password check
        if password != user.password:
            raise serializers.ValidationError("Invalid email or password.")

        data['user'] = user
        return data
