from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Todolist, User
from django.utils import timezone
class LoginSerializers(serializers.Serializer):
    phonenumber = serializers.CharField()
    password = serializers.CharField(write_only=True)
    sms_kod = serializers.CharField(max_length=4)

    def validate(self, attrs):
        phonenumber = attrs.get("phonenumber")
        password = attrs.get("password")
        sms_kod = attrs.get("sms_kod")

        try:
            user = User.objects.get(phonenumber=phonenumber)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "success": False,
                "detail": "User does not exist"
            })

        if not user.check_password(password):
            raise serializers.ValidationError({
                "success": False,
                "detail": "Password is incorrect"
            })

        if user.sms_kod != sms_kod:
            raise serializers.ValidationError({
                "success": False,
                "detail": "SMS code is incorrect"
            })

        attrs["user"] = user
        return attrs



class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phonenumber', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            phonenumber=validated_data['phonenumber'],
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
class SendSMSSerializer(serializers.Serializer):
    phonenumber = serializers.CharField()