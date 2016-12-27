#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Categories)
admin.site.register(models.Ittag)
admin.site.register(models.ArticleInfo)
admin.site.register(models.ArticleDetail)
admin.site.register(models.ArticleViews)
admin.site.register(models.Comments)
admin.site.register(models.Link)