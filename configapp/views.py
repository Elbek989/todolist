import random

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
from .serializers import ToDoListSerializer, UserCreateSerializer
class LoginUser(APIView):
    @swagger_auto_schema(request_body=LoginSerializers)
    def post(self,request):
        serializer = LoginSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        phonenumber=serializer.validated_data.get("phonenumber")
        sms_kod = serializer.validated_data.get("sms_kod")
        user=User.objects.get(phonenumber=phonenumber,sms_kod=sms_kod)
        token = get_tokens_for_user(user)
        user.sms_kod=None
        user.save()

        return Response(data=token)

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

class UserListView(generics.ListAPIView):
    queryset = User.objects.filter(is_user=True)
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdmin]
class ToDoListViewSet(viewsets.ModelViewSet):
    serializer_class = ToDoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_admin:

            return Todolist.objects.all()
        else:

            return Todolist.objects.filter(user=user, bajarilgan=False)

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_admin:
            serializer.save(user=user, bajarilgan=False)
        else:
            raise PermissionDenied("Sizga task yaratishga ruxsat yo‘q")
class Smspost(APIView):
    @swagger_auto_schema(request_body=SendSMSSerializer)
    def post(self,request):
        serializer = SendSMSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phonenumber=serializer.validated_data['phonenumber']
        user=User.objects.get(phonenumber=phonenumber)
        sms_kod=str(random.randint(1000 , 9999))
        user.sms_kod=sms_kod
        user.save()
        print(sms_kod)

        return Response('print qilindi')
