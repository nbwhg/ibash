#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from ibash import settings
from . import models
import json, utils, os
import uuid

# Create your views here.

def index(request):
    # 生成UUID1
    # value = uuid.uuid1().get_hex()
    # 获取数据库中的记录数目
    all_count = models.ArticleInfo.objects.filter(status=False).count()
    # 最新发表文章列表
    new_articles = models.ArticleInfo.objects.filter(status=False).order_by('-published_date')[:12]
    # 浏览最多文章列表
    hot_articles = models.ArticleViews.objects.filter(article__status=False).order_by('-views')[:12]
    # 博客分类列表
    categories = models.Categories.objects.filter(status=False)
    # 最近的评论列表
    latest_comments = models.Comments.objects.filter(status=False).filter(article__status=False).order_by('-published_date')[:12]
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
    response = render(request, 'frontend/index.html', {
        'article_page': article_page,
        'page_string': page_string,
        'categories': categories,
        'new_articles': new_articles,
        'hot_articles': hot_articles,
        'latest_comments': latest_comments,
        'links': links,
    })
    # 设置cookie
    # response.set_cookie("uid", value)
    return response

def index_cate(request, cate):
    # 生成UUID1
    # value = uuid.uuid1().get_hex()
    all_count = models.ArticleInfo.objects.filter(status=False,categories__url=cate).count()
    # 最新发表文章列表
    new_articles = models.ArticleInfo.objects.filter(status=False).order_by('-published_date')[:12]
    # 浏览最多文章列表
    hot_articles = models.ArticleViews.objects.filter(article__status=False).order_by('-views')[:12]
    # 博客分类列表
    categories = models.Categories.objects.filter(status=False)
    # 最近的评论列表
    latest_comments = models.Comments.objects.filter(status=False).filter(article__status=False).order_by('-published_date')[:12]
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
    response = render(request, 'frontend/index_cate.html', {
        'article_page': article_page,
        'page_string': page_string,
        'categories': categories,
        'new_articles': new_articles,
        'hot_articles': hot_articles,
        'latest_comments': latest_comments,
        'links': links,
    })
    # response.set_cookie("uid", value)
    return response

def detail(request, article_id):
    article = get_object_or_404(models.ArticleInfo, pk=article_id)
    # 最新发表文章列表
    new_articles = models.ArticleInfo.objects.filter(status=False).order_by('-published_date')[:12]
    # 浏览最多文章列表
    hot_articles = models.ArticleViews.objects.filter(article__status=False).order_by('-views')[:12]
    # 博客分类列表
    categories = models.Categories.objects.filter(status=False)
    # 最近的评论列表
    latest_comments = models.Comments.objects.filter(status=False).filter(article__status=False).order_by('-published_date')[:12]
    # 友情链接列表
    links = models.Link.objects.filter(status=False)
    # 读取cookie
    uid_value = request.COOKIES.get('uid')
    # 如果直接打开详情页,则不存在cookie,那么直接增加1次浏览量,并写入cookie
    if uid_value is None:
        uid_value = uuid.uuid1().get_hex()
    if uid_value != article.articleviews.uid:
        # 增加一个浏览量
        article.articleviews.views += 1
        # 增加记录
        article.articleviews.uid = uid_value
        article.articleviews.save()
    response = render(request, 'frontend/detail.html', {
        'article': article,
        'categories': categories,
        'new_articles': new_articles,
        'hot_articles': hot_articles,
        'latest_comments': latest_comments,
        'links': links,
    })
    response.set_cookie("uid", uid_value, path="/")
    return response

def comments(request, article_id):
    '''评论处理'''
    timez = request.environ['TZ'] # 这里的时区上线后应该改为settings.TIME_ZONE, 或者直接字符串
    if request.method == 'GET':
        '''请求评论'''
        comment_list = models.Comments.objects.filter(article__id=article_id, status=False)
        comment_tree = utils.handle_comm(comment_list, timez)
        return HttpResponse(json.dumps(comment_tree, default=utils.json_date_handler))
    elif request.method == 'POST':
        for vcode_obj in models.Vcode.objects.all():
            if request.POST['vcode'].upper() == vcode_obj.vcode:
                # 评论提交后再做一次验证,如果验证整个才会入库
                try:
                    vcode_obj.delete()
                except:
                    pass
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
        vcode_obj = vcodeobj.gencode()
        return HttpResponse(vcode_obj.vcodefilename)
    elif request.method == 'POST':
        '''验证验证码'''
        try:
            vcode_obj = get_object_or_404(models.Vcode, vcodefilename=os.path.basename(request.POST['name']))
        except Exception,e:
            vcode_obj = None
        if vcode_obj is not None and vcode_obj.vcode == request.POST['inputvcode'].upper():
            status = "0"
            '''验证成功不删除验证码的数据,只删除验证码图片,等真正提交评论的时候再次验证成功后才会删除验证码'''
            if os.path.isfile(os.path.join(settings.VCODE, os.path.basename(request.POST['name']))):
                '''删除验证码图片'''
                os.remove(os.path.join(settings.VCODE, os.path.basename(request.POST['name'])))
        else:
            status = "1"
            try:
                vcode_obj.delete()
            except:
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
