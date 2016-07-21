#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template
register = template.Library()

@register.filter
def custom_make_list(value):
    '''处理博文标签,将博文标签由字符串转成数组'''
    tag_list = value.strip().split('|')
    return tag_list