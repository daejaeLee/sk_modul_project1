# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

class CustomUser(AbstractUser):  #
    name = models.CharField(max_length=100) 
    email = models.EmailField(unique=True)
    # password = models.CharField(max_length=100) # 기본 제공


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()  # 커스텀 매니저 설정

    class Meta:
        db_table = 'users'  # 데이터베이스 테이블 이름 설정
