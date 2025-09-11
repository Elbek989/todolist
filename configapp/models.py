from tkinter.constants import CASCADE

from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class CustomUserManager(BaseUserManager):
    def create_user(self, phonenumber, password=None, **extra_fields):
        if not phonenumber:
            raise ValueError('raqam kiritish shart')
        user = self.model(phonenumber=phonenumber, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phonenumber, password, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser admin bo‘lishi kerak')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser staff bo‘lishi kerak')
        return self.create_user(phonenumber, password, **extra_fields)



class User(AbstractUser, PermissionsMixin):
    username = None
    phone_regex= RegexValidator(
                regex=r'^\+998\d{9}$',
                message='Telefon raqam +998 bilan boshlanishi va jami 13 ta belgidan iborat bo‘lishi kerak. Masalan: +998901234567')
    name=models.CharField(max_length=50,null=True)
    surname=models.CharField(max_length=50,null=True)

    phonenumber = models.CharField(validators=[phone_regex],max_length=13, unique=True)

    sms_kod=models.CharField(max_length=4,null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phonenumber

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
