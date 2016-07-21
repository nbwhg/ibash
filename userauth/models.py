#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, name and password.
        create_user方法接受的参数是创建用户时所有必填字段
        UserManager重写下两个create方法
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),# normalize_email可以将email地址转换为小写,使其规范化
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(email,
            password=password,
            name=name,
        )
        user.is_admin = True #和模型字段中的定义一定要匹配
        user.save(using=self._db)
        return user

class MyUserAuth(AbstractBaseUser):
    """
    AbstractBaseUser提供一个用户模型的核心实现,包括密码和token重置,必须提供一些关键的实现细节
    AbstractBaseUser已经有password, last_login,所以密码这些就不用费心了
    """
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(u'用户是否激活', default=True)
    is_admin = models.BooleanField(u'是否是管理员', default=False)
    name = models.CharField(u'User Name', max_length=32)
    job = models.CharField(u'职位', max_length=32, default=None, blank=True, null=True)
    note = models.TextField(u'备注', blank=True, null=True, default=None)
    date_joined = models.DateTimeField(u'加入时间', auto_now_add=True)

    # 由于get_username用到了self.USERNAME_FIELD,所以需要指明哪个字段为用户名
    USERNAME_FIELD = 'email' #标识使用哪个字段作为登录的用户名,并且该字段的每个值必须是唯一的
    REQUIRED_FIELDS = ['name'] #表示在创建用户的时候,必须要填写的字段

    # get_short_name,get_full_name需要实现,否则会抛异常
    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        verbose_name = u'用户信息' # 在admin界面中显示的内容
        verbose_name_plural = u"用户信息" #同上,为复数形式的显示内容

    def __unicode__(self):
        return self.name

    # 如果你的User定义了不同的字段, 你就要去自定义一个管理器，它继承自BaseUserManager并提供两个额外的方法:create_user和create_superuser
    objects = UserManager()#实质上就是objects就是一个类属性,这个类属性是UserManager类的一个实例