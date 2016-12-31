#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views
from ueditor import views as ueviews

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^login/$', views.account_login, name='login'),
    url(r'^logout/$', views.account_logout, name='logout'),
    url(r'^links/$', views.links, name='links'),
    url(r'^backlists/$', views.backlists, name='backlists'),
    url(r'^upload_pic/$', views.upload_pic, name='upload_pic'),
    url(r'^create_article/$', views.create_article, name='create_article'),
    url(r'^article_manage/$', views.article_manage, name='article_manage'),
    url(r'^option_delete/$', views.option_delete, name='option_delete'),
    url(r'^recovery_article/$', views.recovery_article, name='recovery_article'),
    url(r'^option_changecate/$', views.option_changecate, name='option_changecate'),
    url(r'^option_changetag/$', views.option_changetag, name='option_changetag'),
    url(r'^already_delete_article/$', views.already_delete_article, name='already_delete_article'),
    url(r'^comment_content/$', views.comment_content, name='comment_content'),
    url(r'^comment_manage/$', views.comment_manage, name='comment_manage'),
    url(r'^comment_update_status/$', views.comment_update_status, name='comment_update_status'),
    url(r'^categories_manage/$', views.categories_manage, name='categories_manage'),
    url(r'^tags_manage/$', views.tags_manage, name='tags_manage'),
    url(r'^load/$', views.load, name='load'),
    url(r'^ueditor_config/$', ueviews.customConfig),
]
