#!/usr/bin/env python
# -*- coding: utf-8 -*-
from frontend import models as frontend_models
from django.db import transaction
from django.utils import timezone
from ibash import settings
import os, re, random

class ArticleGen(object):
    '''创建修改文章'''
    def __init__(self, request):
        self.__title = request.POST['title']
        self.__description = request.POST['description']
        self.__tags = request.POST['tags']
        self.__content = request.POST['content']
        self.__category_id = request.POST.getlist('category_id[]')
        self.__author_id = request.user.id
        self.__modify_date = timezone.now()

    @transaction.atomic
    # 开启一个事务
    def create(self):
        self.__articleinfo = frontend_models.ArticleInfo(
            title=self.__title,
            description=self.__description,
            tags=self.__tags,
            author_id=self.__author_id,
            head_img=genpic(self.__content),
        )
        self.__articleinfo.save()
        self.__articleinfo.categories.add(*self.__category_id)
        self.__articledetail = frontend_models.ArticleDetail(
            article=self.__articleinfo,
            content=self.__content,
        )
        self.__articledetail.save()
        self.__articleviews = frontend_models.ArticleViews(
            article=self.__articleinfo,
            views=0,
        )
        self.__articleviews.save()
        return u'文章 " ' + self.__title + u' " 创建成功!'

def genpic(content):
    # 利用正则匹配生成head img 图片
    re_obj = re.compile(r'<img src="(.*)"/>')
    if re_obj.search(content):
        # 搜索匹配标签
        pic_url = re_obj.search(content).group(1)
        if re.match(r'^/image/(.*)', pic_url):
            # 判断匹配链接是否是本地图片,匹配准确的图片地址
            head_img=re.match(r'^/image/(.*\.(jpg|png|gif|bmp|jpeg))', pic_url).group(1)
        else:
            head_img=u'article/head_img%d.png' % random.choice([1, 2, 3])
    else:
        head_img = u'article/head_img%d.png' % random.choice([1, 2, 3])
    return head_img


def upload_pic(file_obj):
    '''处理文件上传'''
    upload_dir = '%s/%s' % (settings.MEDIA_ROOT, settings.UPLOAD_PIC_TO)
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)
    with open('%s/%s' % (upload_dir, file_obj.name), 'wb') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
    return file_obj.name
