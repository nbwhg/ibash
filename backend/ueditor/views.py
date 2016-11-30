#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from . import config
from ibash import settings

@csrf_exempt
@login_required
def customConfig(request):
    params = request.GET
    if params['action'] == 'uploadimage':
        return ueditor_ImgUp(request)
    return HttpResponse(json.dumps(config.config))


def __myuploadfile(fileObj, source_pictitle, source_filename, fileorpic='pic'):
    """ 一个公用的上传文件的处理 """
    upload_dir = '%s/%s' % (settings.MEDIA_ROOT, settings.UPLOAD_PIC_TO)
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)
    with open('%s/%s' % (upload_dir, fileObj.name), 'wb') as destination:
        for chunk in fileObj.chunks():
            destination.write(chunk)
    real_url = '%s%s%s' % (settings.MEDIA_URL, settings.UPLOAD_PIC_TO, fileObj.name)
    myresponse = "{'url':'%s','original':'%s','type':'%s','state':'%s','size':'%s'}" % (real_url,"aaa","jpg","SUCCESS",5)
    return_info = {
                    'url': real_url,
                    'original': "AA",
                    'type': "jpg",
                    'state': "SUCCESS",
                    'size': 5
            }
    return json.dumps(return_info, ensure_ascii=False)

def ueditor_ImgUp(request):
    """ 上传图片 """
    fileObj = request.FILES.get('upfile', None)
    source_pictitle = request.POST.get('pictitle', '')
    source_filename = request.POST.get('fileName', '')
    response = HttpResponse()
    myresponse = __myuploadfile(fileObj, source_pictitle, source_filename, 'pic')
    response.write(myresponse)
    return response
