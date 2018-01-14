#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from userauth.models import MyUserAuth

# Create your models here.

class Categories(models.Model):
    name = models.CharField(u'类别名称', max_length=55, unique=True)
    url = models.CharField(u'访问地址', max_length=55, unique=True)
    status = models.BooleanField(u'是否删除', default=False)
    category_type_choice = (
        ('N', 'normal'),
        ('P', 'project'),
    )
    type = models.CharField(u'分类方式', choices=category_type_choice, max_length=2)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u'博客分类'
        verbose_name_plural = u"博客分类"

class Ittag(models.Model):
    name = models.CharField(u'标签名称', max_length=55, unique=True)
    status = models.BooleanField(u'是否删除', default=False)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u'技术标签'
        verbose_name_plural = u"技术标签"

class ArticleInfo(models.Model):
    title = models.CharField(u'文章标题', max_length=100)
    head_img = models.ImageField(u'链接图片', upload_to="article/")
    description = models.CharField(u'文章描述', max_length=255)
    tags = models.CharField(u'文章标签', max_length=255)#关键字以|分隔
    author = models.ForeignKey(MyUserAuth, on_delete=models.DO_NOTHING)
    categories = models.ManyToManyField('Categories')
    ittags = models.ManyToManyField(Ittag)
    published_date = models.DateTimeField(u'创建时间', auto_now_add=True)
    modify_date = models.DateTimeField(u'最后修改时间', auto_now=True)
    status = models.BooleanField(u'是否删除', default=False)
    istop = models.BooleanField(u'是否置顶', default=False)
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = u'文章信息'
        verbose_name_plural = u'文章信息'

class ArticleDetail(models.Model):
    article = models.OneToOneField('ArticleInfo', on_delete=models.DO_NOTHING)
    content = models.TextField()
    def __unicode__(self):
        return "%s==>content" % self.article.title
    class Meta:
        verbose_name = u'文章正文'
        verbose_name_plural = u'文章正文'

class ArticleViews(models.Model):
    article = models.OneToOneField('ArticleInfo', on_delete=models.DO_NOTHING)
    uid = models.CharField(u'用户cookie', max_length=32)
    views = models.IntegerField(u'浏览量', default=0)
    def __unicode__(self):
        return "%s==>%s" % (self.article.title, self.views)
    class Meta:
        verbose_name = u'浏览量'
        verbose_name_plural = u'浏览量'

class Comments(models.Model):
    nickname = models.CharField(u'昵称', max_length=100)
    email = models.EmailField(u'联系邮箱', max_length=255)
    client_ip = models.GenericIPAddressField(u'IP地址')
    client_type = models.CharField(u'浏览器类型', max_length=255)
    published_date = models.DateTimeField(u'评论时间', auto_now_add=True)
    comment = models.TextField(u'评论内容', max_length=2048)
    status = models.BooleanField(u'是否删除', default=False)
    article = models.ForeignKey('ArticleInfo')
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='pid', on_delete=models.DO_NOTHING, verbose_name=u'父级评论')
    def __unicode__(self):
        return self.email
    class Meta:
        verbose_name = u'评论'
        verbose_name_plural = u'评论'

class Link(models.Model):
    url = models.URLField(u'链接地址')
    name = models.CharField(u'链接名称', max_length=55, unique=True)
    contact = models.CharField(u'链接负责人', max_length=55)
    contact_qq = models.CharField(u'链接负责人QQ', max_length=20, null=True, blank=True)
    contact_email = models.EmailField(u'链接负责人邮箱地址', max_length=255)
    join_date = models.DateTimeField(u'加入时间', auto_now_add=True)
    status = models.BooleanField(u'是否删除', default=False)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u'友情链接'
        verbose_name_plural = u'友情链接'

class Vcode(models.Model):
    vcodefilename = models.CharField(u'验证码图片名称', max_length=20, unique=True)
    vcode = models.CharField(u'验证码', max_length=5)
    def __unicode__(self):
        return self.vcode
    class Meta:
        verbose_name = u'验证码'
        verbose_name_plural = u'验证码'