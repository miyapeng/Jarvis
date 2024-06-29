from django.db import models


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=50, verbose_name='用户名')
    email = models.CharField(max_length=50, unique=True, verbose_name='邮箱')
    password = models.CharField(max_length=50, verbose_name='密码')
