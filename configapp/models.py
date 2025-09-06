from tkinter.constants import CASCADE

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username kiritish shart')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser admin bo‘lishi kerak')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser staff bo‘lishi kerak')
        return self.create_user(username, password, **extra_fields)



class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    @property
    def is_superuser(self):
        return self.is_admin

class Todolist(models.Model):
    title=models.CharField(max_length=50)
    bajarilgan=models.BooleanField(default=False)
    done_time = models.DateTimeField(null=True, blank=True)

    user=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# Create your models here.
