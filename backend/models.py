#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.

class Cpuload(models.Model):
    timestamp = models.DateTimeField(u'时间戳')
    oneminutes = models.DecimalField(u'1分钟', max_digits=5, decimal_places=2)
    fiveminutes = models.DecimalField(u'5分钟', max_digits=5, decimal_places=2)
    fifteenminutes = models.DecimalField(u'15分钟', max_digits=5, decimal_places=2)
    def __unicode__(self):
        return self.oneminutes

class Diskinfo(models.Model):
    timestamp = models.DateTimeField(u'时间戳')
    total = models.BigIntegerField(u'总共')
    available = models.BigIntegerField(u'可用')
    used = models.BigIntegerField(u'已用')
    def __unicode__(self):
        return self.used

class Meminfo(models.Model):
    timestamp = models.DateTimeField(u'时间戳')
    total = models.BigIntegerField(u'总共')
    memfree = models.BigIntegerField(u'可用')
    used = models.BigIntegerField(u'已用')
    def __unicode__(self):
        return self.used