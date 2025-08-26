from django.contrib.auth import get_user_model
from djoser.serializers import (
  UserCreateSerializer as DjoserUserCreateSerialzier,
  UserSerializer as DjoserUserSerializer,
)


User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerialzier):
  class Meta(DjoserUserCreateSerialzier.Meta):
    model = User
    fields = [
      "email", "username", "password", "first_name", "last_name", "id_no", "security_question", "security_answer",
    ]
  
  def create(self, validated_data):
    user = User.objects.create_user(**validated_data)
    return user


class UserSerializer(DjoserUserSerializer):
  class Meta(DjoserUserSerializer.Meta):
    model = User
    fields = [
      "email", "username", "first_name", "last_name", "id_no", "full_name", "role"
    ]