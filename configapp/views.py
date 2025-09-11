import random
from django.core.cache import cache

from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from .make_token import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics, permissions
from .models import Todolist, User
from .serializers import *


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdmin]


# class ToDoListViewSet(viewsets.ModelViewSet):
#     serializer_class = ToDoListSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         if user.is_admin :
#             return Todolist.objects.all()
#
#         return Todolist.objects.filter(user=user, bajarilgan=False)
#
#
#     def perform_create(self, serializer):
#         if self.request.user.is_admin:
#             serializer.save(user=self.request.user,bajarilgan = False)
#         else:
#             raise PermissionDenied("Sizga task yaratishga ruxsat yo‘q")


    def perform_create(self, serializer):
        user = self.request.user

        if user.is_admin:
            serializer.save(user=user, bajarilgan=False)
        else:
            raise PermissionDenied("Sizga task yaratishga ruxsat yo‘q")


class Smspost(APIView):
    @swagger_auto_schema(request_body=SendSMSSerializer)
    def post(self, request):
        serializer = SendSMSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phonenumber = serializer.validated_data['phonenumber']

        sms_kod = str(random.randint(1000, 9999))

        cache.set(f"sms_code_{phonenumber}", sms_kod, timeout=600)

        print(f"{phonenumber} raqamiga SMS kodi: {sms_kod}")

        return Response({"success": True, "message": "SMS kodi yuborildi"}, status=status.HTTP_200_OK)

class VerifyCodeAPIView(APIView):
    @swagger_auto_schema(request_body=VerifyCodeSerializer)
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"success": True, "message": "Telefon raqam tasdiqlandi"})
class RegisterUserAPIView(APIView):
    @swagger_auto_schema(request_body=UserCreateSerializer)
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phonenumber = serializer.validated_data.get("phonenumber")

        verified = cache.get(f"phone_verified_{phonenumber}")
        if not verified:
            return Response(
                {"success": False, "detail": "Telefon raqamingiz hali tasdiqlanmagan"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Userni yaratamiz
        user = serializer.save()

        # SMS tasdiq flagini o‘chirib tashlash (bir martalik)
        cache.delete(f"phone_verified_{phonenumber}")

        return Response(
            {"success": True, "message": "Foydalanuvchi yaratildi", "user_id": user.id},
            status=status.HTTP_201_CREATED
        )

class LoginUser(APIView):
    @swagger_auto_schema(request_body=LoginSerializers)
    def post(self, request):
        serializer = LoginSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token = get_tokens_for_user(user)

        cache.delete(f"sms_code_{user.phonenumber}")

        return Response(token, status=status.HTTP_200_OK)
