#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from ibash import settings
from . import models
import json, utils, os

# 用于存放验证码验证信息,验证完成不论成功或者失败都会删除对应的key,value
# 存储格式{'验证码文件名': '验证码'}
vcodedic = {}
# Create your views here.

def index(request):
    # 获取数据库中的记录数目
    all_count = models.ArticleInfo.objects.filter(status=False).count()
    # 最新发表文章列表
    new_articles = models.ArticleInfo.objects.filter(status=False).order_by('-published_date')[:12]
    # 浏览最多文章列表
    hot_articles = models.ArticleViews.objects.filter(article__status=False).order_by('-views')[:12]
    # 博客分类列表
    categories = models.Categories.objects.filter(status=False)
    # 最近的评论列表
    latest_comments = models.Comments.objects.filter(article__status=False).order_by('-published_date')[:12]
    # 友情链接列表
    links = models.Link.objects.filter(status=False)
    # 获取当前请求的页数
    try:
        page = int(request.GET.get('page'))
    except Exception,e:
        page = 1
    # 分页对象
    pageobj = utils.PageInfo(page, all_count)
    # 获取当前页面的文章对象
    article_page = models.ArticleInfo.objects.filter(status=False).order_by('-modify_date')[pageobj.start:pageobj.end]
    # 分页字符串
    page_string = utils.Pager(page, pageobj.all_page)
    return render(request, 'frontend/index.html', {
        'article_page': article_page,
        'page_string': page_string,
        'categories': categories,
        'new_articles': new_articles,
        'hot_articles': hot_articles,
        'latest_comments': latest_comments,
        'links': links,
    })

def index_cate(request, cate):
    all_count = models.ArticleInfo.objects.filter(status=False,categories__url=cate).count()
    # 最新发表文章列表
    new_articles = models.ArticleInfo.objects.filter(status=False).order_by('-published_date')[:12]
    # 浏览最多文章列表
    hot_articles = models.ArticleViews.objects.filter(article__status=False).order_by('-views')[:12]
    # 博客分类列表
    categories = models.Categories.objects.filter(status=False)
    # 最近的评论列表
    latest_comments = models.Comments.objects.filter(article__status=False).order_by('-published_date')[:12]
    # 友情链接列表
    links = models.Link.objects.filter(status=False)
    try:
        page = int(request.GET.get('page'))
    except Exception,e:
        page = 1
    # 分页对象
    pageobj = utils.PageInfo(page, all_count)
    # 获取当前页面的文章对象
    article_page = models.ArticleInfo.objects.filter(status=False,categories__url=cate).order_by('-modify_date')[pageobj.start:pageobj.end]
    # 分页字符串
    page_string = utils.Pager(page, pageobj.all_page)
    return render(request, 'frontend/index_cate.html', {
        'article_page': article_page,
        'page_string': page_string,
        'categories': categories,
        'new_articles': new_articles,
        'hot_articles': hot_articles,
        'latest_comments': latest_comments,
        'links': links,
    })

def detail(request, article_id):
    article = get_object_or_404(models.ArticleInfo, pk=article_id)
    # 最新发表文章列表
    new_articles = models.ArticleInfo.objects.filter(status=False).order_by('-published_date')[:12]
    # 浏览最多文章列表
    hot_articles = models.ArticleViews.objects.filter(article__status=False).order_by('-views')[:12]
    # 博客分类列表
    categories = models.Categories.objects.filter(status=False)
    # 最近的评论列表
    latest_comments = models.Comments.objects.filter(article__status=False).order_by('-published_date')[:12]
    # 友情链接列表
    links = models.Link.objects.filter(status=False)
    # 增加一个浏览量
    article.articleviews.views += 1
    article.articleviews.save()
    return render(request, 'frontend/detail.html', {
        'article': article,
        'categories': categories,
        'new_articles': new_articles,
        'hot_articles': hot_articles,
        'latest_comments': latest_comments,
        'links': links,
    })

def comments(request, article_id):
    '''评论处理'''
    timez = request.environ['TZ']
    if request.method == 'GET':
        '''请求评论'''
        comment_list = models.Comments.objects.filter(article__id=article_id, status=False)
        comment_tree = utils.handle_comm(comment_list, timez)
        return HttpResponse(json.dumps(comment_tree, default=utils.json_date_handler))
    elif request.method == 'POST':
        for item in vcodedic.iteritems():
            if request.POST['vcode'].upper() in item:
                # 评论提交后再做一次验证,如果验证整个才会入库
                del vcodedic[item[0]]
                if len(request.POST['comment']) < 5:
                    # 再做一次评论长度的验证
                    res = "2"
                    break
                comment_obj = utils.SaveComment(request, article_id)
                comment_res = comment_obj.create()
                res = json.dumps(utils.handle_single_comm(comment_res, timez), default=utils.json_date_handler)
                break
        else:
            res = "1"
        return HttpResponse(res)

def genvcode(request):
    '''验证码处理'''
    if request.method == 'GET':
        '''请求验证码'''
        vcodeobj = utils.VerifyCode(5)
        callbackdata  = vcodeobj.gencode()
        vcodedic[callbackdata['name']] = callbackdata['vcode']
        return HttpResponse(callbackdata['name'])
    elif request.method == 'POST':
        '''验证验证码'''
        if vcodedic.has_key(os.path.basename(request.POST['name'])) and vcodedic[os.path.basename(request.POST['name'])] == request.POST['inputvcode'].upper():
            status = "0"
            #del vcodedic[os.path.basename(request.POST['name'])]# 删除字典中的值
            if os.path.isfile(os.path.join(settings.VCODE, os.path.basename(request.POST['name']))):
                '''删除验证码图片'''
                os.remove(os.path.join(settings.VCODE, os.path.basename(request.POST['name'])))
        else:
            status = "1"
            try:
                del vcodedic[os.path.basename(request.POST['name'])]# 删除字典中的值
            except KeyError:
                pass
            if os.path.isfile(os.path.join(settings.VCODE, os.path.basename(request.POST['name']))):
                '''删除验证码图片'''
                os.remove(os.path.join(settings.VCODE, os.path.basename(request.POST['name'])))
        return HttpResponse(json.dumps(status))

def search(request):
    # 博客分类列表
    categories = models.Categories.objects.all()
    searchkey = request.POST['searchkey']
    articlelist = models.ArticleInfo.objects.filter(status=False).filter(Q(title__icontains=searchkey)|Q(description__icontains=searchkey)|Q(tags__icontains=searchkey)|Q(articledetail__content__icontains=searchkey))
    return render(request, 'frontend/search_result.html', {
        'categories': categories,
        'artilelist': articlelist,
        'keyword': searchkey,
    })