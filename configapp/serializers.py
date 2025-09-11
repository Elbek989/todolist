from rest_framework import serializers
from django.core.cache import cache
from .models import *
import random
class SendSMSSerializer(serializers.Serializer):
    phonenumber = serializers.CharField()

    def validate_phonenumber(self, value):
        if not value.startswith('+998') :
            raise serializers.ValidationError("Telefon raqam noto‘g‘ri formatda.")
        return value
class LoginSerializers(serializers.Serializer):
    phonenumber = serializers.CharField()

    def validate(self, attrs):
        phonenumber = attrs.get("phonenumber")

        try:
            user = User.objects.get(phonenumber=phonenumber)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "success": False,
                "detail": "Bu raqam bilan foydalanuvchi topilmadi"
            })

        attrs["user"] = user
        return attrs


class VerifyCodeSerializer(serializers.Serializer):
    phonenumber = serializers.CharField()
    sms_kod = serializers.CharField(max_length=4)

    def validate(self, attrs):
        phonenumber = attrs.get("phonenumber")
        sms_kod = attrs.get("sms_kod")

        cached_code = cache.get(f"sms_code_{phonenumber}")
        if cached_code != sms_kod:
            raise serializers.ValidationError("SMS kodi noto‘g‘ri yoki eskirgan")


        cache.set(f"phone_verified_{phonenumber}", True, timeout=600)
        return attrs
class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [ 'phonenumber', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            phonenumber=validated_data['phonenumber'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            is_user=True
        )
        return user