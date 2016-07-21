#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^article/(?P<article_id>\d+)/$', views.detail, name='article_detail'),
    url(r'^comments/(?P<article_id>\d+)/$', views.comments, name='comments'),
    url(r'^vcode/$', views.genvcode, name='vcode'),
    url(r'^search/$', views.search, name='search'),
    url(r'^(?P<cate>\w+)/$', views.index_cate, name='index_cate'),
]
