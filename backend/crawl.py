#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, sys, os
import django
from django.utils import timezone

BaseDir = '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]) #获取django项目的根目录
sys.path.append(BaseDir) #将django项目的根目录添加到python系统的path路径
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ibash.settings") #声明环境变量,等于export DJANGO_SETTINGS_MODULE=ibash.settings
django.setup()# 允许外部的脚本调用django的模块

from backend import models

def get_cpuload():
    if sys.platform == 'linux2':
        with open('/proc/loadavg') as fn:
            res = fn.readline().split()[:3]
    elif sys.platform == 'darwin':
        import subprocess
        cpuload = subprocess.Popen("uptime", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = cpuload.communicate()
        res = stdoutput.split()[-3:]
    load_obj = models.Cpuload(timestamp=timezone.now(), oneminutes=res[0], fiveminutes=res[1], fifteenminutes=res[2])
    load_obj.save()

def get_diskinfo():
    pass

def get_meminfo():
    pass

if __name__ == '__main__':
    while True:
        get_cpuload()
        get_diskinfo()
        get_meminfo()
        time.sleep(60)