from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Todolist, User
from django.utils import timezone
class LoginSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self,attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "success":False,
                    "detail":"User does not exist"
                }
            )
        auth_user = authenticate(username = user.username,password = password)
        if auth_user is None:
            raise serializers.ValidationError(
                {
                    "success":False,
                    "detail":"Username or password is invalid"
                }
            )
        attrs["user"] = auth_user
        return attrs



class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            is_user=True
        )
        return user


class ToDoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todolist
        fields = ['id', 'title', 'bajarilgan', 'done_time', 'user']
        read_only_fields = ['done_time']

    def create(self, validated_data):
        request = self.context.get('request')

        if request and request.user.is_user:
            raise serializers.ValidationError("Oddiy foydalanuvchi task qo‘sha olmaydi")


        if 'user' not in validated_data:
            raise serializers.ValidationError("Taskni qaysi userga berishni belgilang")

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')

        if request and request.user.is_user:

            instance.bajarilgan = True
            instance.done_time = timezone.now()
            instance.save()
            return instance


        return super().update(instance, validated_data)