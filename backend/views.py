#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from frontend import models as frontend_models
from backend import models as backend_models
from userauth import models as userauth_models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models import Sum
import utils, json, datetime, pytz, os
from django.utils import timezone
from ibash import settings

# Create your views here.

def account_login(request):
    '''用户登录处理'''
    if request.method == 'GET':
        '''GET方法表示请求页面'''
        return render(request, 'backend/login.html')
    elif request.method == 'POST':
        '''POST方法表示请求验证'''
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                '''如果用户是激活状态的'''
                login(request, user)
                return HttpResponseRedirect('/backend/')
            else:
                login_info = 'user %s is disabled!' % email
        else:
            login_info = 'invalid user or password, login error!'
        return render(request, 'backend/login.html', {'login_info': login_info})

def account_logout(request):
    '''用户注销操作'''
    logout(request)
    return HttpResponseRedirect('/backend/')

@login_required
def index(request):
    '''返回前端所需要的变量'''
    # 求文章数量
    article_count = frontend_models.ArticleInfo.objects.count()
    # 求评论数量
    comment_count = frontend_models.Comments.objects.count()
    # 聚合操作, 求总共的浏览量
    view_count = frontend_models.ArticleViews.objects.aggregate(Sum('views'))
    # 求图片数量
    pic_count = len(os.listdir('%s/%s' % (settings.MEDIA_ROOT, settings.UPLOAD_PIC_TO)))
    return render(request, 'backend/index.html', {
        'article_count': article_count,
        'comment_count': comment_count,
        'view_count': view_count,
        'pic_count': pic_count,
    })

@login_required
def create_article(request):
    '''创建文章操作'''
    if request.method == 'GET':
        '''如果是GET则是请求创建文章的页面'''
        categories = frontend_models.Categories.objects.filter(status=False)
        if request.GET.get('article_id'):
            '''如果有article_id,则加载文章的内容,用于重新编辑修改文章内容'''
            article_obj = frontend_models.ArticleInfo.objects.get(pk=request.GET.get('article_id'))
            return render(request, 'backend/create_article.html', {'categorys': categories, 'article_obj': article_obj})
        else:
            return render(request, 'backend/create_article.html', {'categorys': categories})
    elif request.method == 'POST':
        '''如果是POST则是请求创建文章'''
        if request.POST.get('obj') == u'create':
            '''创建文章'''
            article_obj = utils.ArticleGen(request)
            res = article_obj.create()
            return HttpResponse(res)
        else:
            '''修改文章'''
            article_obj = frontend_models.ArticleInfo.objects.get(pk=request.POST.get('obj'))
            article_obj.title = request.POST.get('title')
            article_obj.description = request.POST.get('description')
            article_obj.tags = request.POST.get('tags')
            article_obj.articledetail.content = request.POST.get('content')
            article_obj.categories.clear()
            article_obj.categories.add(*request.POST.getlist('category_id[]'))
            article_obj.modify_date = timezone.now()
            article_obj.save()
            article_obj.articledetail.save()
            return HttpResponse(u"%s 修改成功!" % article_obj.title)

@login_required
def article_manage(request):
    '''文章管理的操作'''
    # 以下两个变量用于博文筛选
    categories = frontend_models.Categories.objects.filter(status=False)
    author_all = userauth_models.MyUserAuth.objects.all()
    if request.method == 'GET':
        '''GET方法表示请求页面并返回所有的文章'''
        # 以下变量前台筛选框需要
        request_method = 'get'
        searchkey = ''
        a_id = ''
        category_id = ''
        pubdate = ''
        moddate = ''
        # 获取所有文章列表
        article_list = frontend_models.ArticleInfo.objects.filter(status=False).order_by('-modify_date', 'published_date')
        paginator = Paginator(article_list, 16)
        # 返回总页数
        page_numbers = paginator.num_pages
        # 获取当前请求的页数,通过GET方法获取
        page = request.GET.get('page')
    elif request.method == 'POST':
        '''POST方法表示筛选文章'''
        # 以下变量是必须的,请求类型前台需要
        request_method = 'post'
        searchkey = request.POST['searchkey']
        a_id = request.POST['author_id']
        pubdate = request.POST['published_date']
        moddate = request.POST['modify_date']
        # 时间转换,将字符串转换成时间对象
        if moddate != u'':
            m_date = datetime.datetime.strptime(moddate, "%Y-%m-%d").replace(tzinfo=pytz.timezone(request.environ['TZ'])).astimezone(pytz.timezone('UTC'))
        else:
            m_date = moddate
        if pubdate != u'':
            p_date = datetime.datetime.strptime(pubdate, "%Y-%m-%d").replace(tzinfo=pytz.timezone(request.environ['TZ'])).astimezone(pytz.timezone('UTC'))
        else:
            p_date = pubdate
        category_id = request.POST['category_id']
        # 筛选结果,可以对结果集再次filter
        if category_id != u'all':
            article_list = frontend_models.ArticleInfo.objects.filter(status=False).filter(categories__id=category_id).order_by('-modify_date', 'published_date')
        else:
            article_list = frontend_models.ArticleInfo.objects.filter(status=False).order_by('-modify_date', 'published_date')
        if a_id != u'all':
            article_list = article_list.filter(author__id=a_id).order_by('-modify_date', 'published_date')
        if p_date != u'':
            article_list = article_list.filter(published_date__gt=p_date).order_by('-modify_date', 'published_date')
        if m_date != u'':
            article_list = article_list.filter(modify_date__gt=m_date).order_by('-modify_date', 'published_date')
        if searchkey != u'':
            article_list = article_list.filter(Q(title__icontains=searchkey)|Q(description__icontains=searchkey)|Q(tags__icontains=searchkey)|Q(articledetail__content__icontains=searchkey)).order_by('-modify_date', 'published_date')
        paginator = Paginator(article_list, 16)
        # 返回总页数
        page_numbers = paginator.num_pages
        # 获取当前请求的页数,筛选过程中页面值的传递使用的是POST方法
        page = request.POST.get('page')
        if page == 'start':
            page = '1'
        elif page == 'end':
            page = page_numbers
    try:
        article_page = paginator.page(page)
    except PageNotAnInteger:
        article_page = paginator.page(1)
    except EmptyPage:
        article_page = paginator.page(paginator.num_pages)
    return render(request, 'backend/article_manage.html', {
        'article_page': article_page,
        'page_numbers': page_numbers,
        'categories': categories,
        'authors': author_all,
        'request_method': request_method,
        'searchkey': searchkey,
        'author_id': a_id,
        'category_id': category_id,
        'modify_date': moddate,
        'published_date': pubdate,
    })

@login_required
def option_delete(request):
    '''批量删除'''
    if request.method == 'POST':
        for aid in request.POST.getlist('delete_objs[]'):
            aobj = frontend_models.ArticleInfo.objects.get(pk=aid)
            aobj.status = True
            aobj.save()#一定要保存
        return HttpResponse("删除成功!")

@login_required
def recovery_article(request):
    '''批量恢复'''
    if request.method == 'POST':
        for aid in request.POST.getlist('delete_objs[]'):
            aobj = frontend_models.ArticleInfo.objects.get(pk=aid)
            aobj.status = False
            aobj.save()#一定要保存
        return HttpResponse("恢复成功!")

@login_required
def option_changecate(request):
    '''批量修改分类'''
    if request.method == 'POST':
        cateobj = frontend_models.Categories.objects.get(pk=request.POST.get('cid'))
        for aid in request.POST.getlist('arr_objs[]'):
            aobj = frontend_models.ArticleInfo.objects.get(pk=aid)
            aobj.categories.clear()
            aobj.categories.add(cateobj)
            aobj.save()#一定要记得保存
        return HttpResponse("修改成功!")

@login_required
def already_delete_article(request):
    '''已删除博文,处理逻辑跟博文管理一模一样'''
    categories = frontend_models.Categories.objects.filter(status=False)
    author_all = userauth_models.MyUserAuth.objects.all()
    if request.method == 'GET':
        # 以下变量前台筛选框需要
        request_method = 'get'
        searchkey = ''
        a_id = ''
        category_id = ''
        pubdate = ''
        moddate = ''
        page = request.GET.get('page')
        article_list = frontend_models.ArticleInfo.objects.filter(status=True).order_by('-modify_date', 'published_date')
        paginator = Paginator(article_list, 16)
        page_numbers = paginator.num_pages
        page = request.GET.get('page')
    elif request.method == 'POST':
        '''POST方法表示筛选文章'''
        # 以下变量是必须的,请求类型前台需要
        request_method = 'post'
        searchkey = request.POST['searchkey']
        a_id = request.POST['author_id']
        pubdate = request.POST['published_date']
        moddate = request.POST['modify_date']
        if moddate != u'':
            m_date = datetime.datetime.strptime(moddate, "%Y-%m-%d").replace(tzinfo=pytz.timezone(request.environ['TZ'])).astimezone(pytz.timezone('UTC'))
        else:
            m_date = moddate
        if pubdate != u'':
            p_date = datetime.datetime.strptime(pubdate, "%Y-%m-%d").replace(tzinfo=pytz.timezone(request.environ['TZ'])).astimezone(pytz.timezone('UTC'))
        else:
            p_date = pubdate
        category_id = request.POST['category_id']
        if category_id != u'all':
            article_list = frontend_models.ArticleInfo.objects.filter(status=True).filter(categories__id=category_id).order_by('-modify_date', 'published_date')
        else:
            article_list = frontend_models.ArticleInfo.objects.filter(status=True).order_by('-modify_date', 'published_date')
        if a_id != u'all':
            article_list = article_list.filter(author__id=a_id).order_by('-modify_date', 'published_date')
        if p_date != u'':
            article_list = article_list.filter(published_date__gt=p_date).order_by('-modify_date', 'published_date')
        if m_date != u'':
            article_list = article_list.filter(modify_date__gt=m_date).order_by('-modify_date', 'published_date')
        if searchkey != u'':
            article_list = article_list.filter(
                Q(title__icontains=searchkey) | Q(description__icontains=searchkey) | Q(tags__icontains=searchkey) | Q(articledetail__content__icontains=searchkey)).order_by(
                '-modify_date', 'published_date')
        paginator = Paginator(article_list, 16)
        # 返回总页数
        page_numbers = paginator.num_pages
        # 获取当前请求的页数,筛选过程中页面值的传递使用的是POST方法
        page = request.POST.get('page')
        if page == 'start':
            page = '1'
        elif page == 'end':
            page = page_numbers
    try:
        article_page = paginator.page(page)
    except PageNotAnInteger:
        article_page = paginator.page(1)
    except EmptyPage:
        article_page = paginator.page(paginator.num_pages)
    return render(request, 'backend/already_delete_article.html', {
        'article_page': article_page,
        'page_numbers': page_numbers,
        'categories': categories,
        'authors': author_all,
        'request_method': request_method,
        'searchkey': searchkey,
        'author_id': a_id,
        'category_id': category_id,
        'modify_date': moddate,
        'published_date': pubdate,
    })

@login_required
def links(request):
    '''链接管理,包含展示链接,批量更改链接的状态,创建和更新某一条链接'''
    if request.method == 'GET':
        '''GET为返回页面'''
        links_list = frontend_models.Link.objects.all()
        if request.GET.get('link_id'):
            '''带要修改的链接对象返回'''
            link_change = frontend_models.Link.objects.get(pk=request.GET.get('link_id'))
            return render(request, 'backend/links.html', {'links': links_list, 'link_change': link_change})
        else:
            '''正常返回'''
            return render(request, 'backend/links.html', {'links': links_list})
    elif request.method == 'POST':
        '''POST为提交操作'''
        if request.POST.get('type') == 'update_link':
            '''仅仅针对链接状态的启用和和停用'''
            for link in request.POST.getlist('obj_lists[]'):
                link_obj = frontend_models.Link.objects.get(pk=link)
                if link_obj.status:
                    link_obj.status = False
                else:
                    link_obj.status = True
                link_obj.save()
            return HttpResponse("更新成功!")
        if request.POST.get('type') == 'create_link':
            if request.POST.get('linktype') == 'create':
                '''创建一个全新的链接'''
                new_link = frontend_models.Link(name=request.POST['name'],
                                                       url=request.POST['linkaddress'],
                                                       contact=request.POST['linkcontact'],
                                                       contact_email=request.POST['linkemail'],
                                                       contact_qq=request.POST['linkqq'])
                new_link.save()
                return HttpResponse(u"%s , 创建成功!" % new_link.name)
            elif request.POST.get('linktype') == 'update':
                '''修改已有的链接'''
                old_link = frontend_models.Link.objects.get(pk=request.POST.get('linkid'))
                old_link.name=request.POST['name']
                old_link.url=request.POST['linkaddress']
                old_link.contact=request.POST['linkcontact']
                old_link.contact_email=request.POST['linkemail']
                old_link.contact_qq=request.POST['linkqq']
                old_link.save()
                return HttpResponse(u"%s , 更新成功!" % old_link.name)


@login_required
def backlists(request):
    '''黑名单'''
    return render(request, 'backend/backlists.html')

@csrf_exempt#让CSRF不做验证
@login_required
def upload_pic(request):
    '''图片上传'''
    if request.method == 'GET':
        '''GET方法为获取图片'''
        pic_list = []
        for i in os.listdir(os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_PIC_TO)):
            pathname = "%s%s%s" % (settings.MEDIA_URL, settings.UPLOAD_PIC_TO,  i)
            timest = datetime.datetime.fromtimestamp(os.stat(os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_PIC_TO, i)).st_ctime).strftime("%Y-%m-%d %T")
            picsize = os.stat(os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_PIC_TO, i)).st_size
            pic_list.append({'name': pathname, 'time': timest, 'picsize': picsize})
        pic_list = sorted(pic_list, key=lambda t: t['time'], reverse=True)# 按照时间排序
        return render(request, 'backend/upload_pic.html', {'pic_list': pic_list})
    elif request.method == 'POST':
        '''POST方法为上传图片'''
        '''处理文件上传'''
        '''在服务器端上传目录要有web服务器的写权限'''
        filename = request.FILES['input44[]']
        obj = utils.upload_pic(filename)
        return HttpResponse(json.dumps({'text': 'success'}))

@login_required
def comment_content(request):
    '''展示评论具体内容'''
    if request.method == 'GET':
        if request.GET.get('comment_id'):
            latest_comment = frontend_models.Comments.objects.get(pk=request.GET.get('comment_id'))
        else:
            latest_comment = frontend_models.Comments.objects.all().order_by('-published_date')[0]
        return render(request, 'backend/comment_content.html', {'latest_comment': latest_comment})

@login_required
def comment_manage(request):
    '''展示所有评论'''
    if request.method == 'GET':
        request_method = 'get'
        searcharticle = u''
        searchcontent = u''
        pubdate = u''
        comment_list = frontend_models.Comments.objects.all().order_by('-published_date')
        paginator = Paginator(comment_list, 16)
        # 返回总页数
        page_numbers = paginator.num_pages
        # 获取当前请求的页数,筛选过程中页面值的传递使用的是POST方法
        page = request.GET.get('page')
    elif request.method == 'POST':
        '''GET方法用于检索评论'''
        # 以下几个变量用于前端页面
        request_method = 'post'
        searcharticle = request.POST['searcharticle']
        searchcontent = request.POST['searchcontent']
        pubdate = request.POST['published_date']
        # 用于时间转换
        if pubdate != u'':
            p_date = datetime.datetime.strptime(pubdate, "%Y-%m-%d").replace(tzinfo=pytz.timezone(request.environ['TZ'])).astimezone(pytz.timezone('UTC'))
        else:
            p_date = pubdate
        # 以下用于检索匹配条件
        if p_date != u'':
            comment_list = frontend_models.Comments.objects.filter(published_date__gt=p_date).order_by('-published_date')
        else:
            comment_list = frontend_models.Comments.objects.all().order_by('-published_date')
        if searcharticle != u'':
            comment_list = comment_list.filter(article__title__icontains=searcharticle).order_by('published_date')
        if searchcontent != u'':
            comment_list = comment_list.filter(comment__icontains=searchcontent).order_by('-published_date')
        # 计算页数
        paginator = Paginator(comment_list, 16)
        # 返回总页数
        page_numbers = paginator.num_pages
        # 获取当前请求的页数,筛选过程中页面值的传递使用的是POST方法
        page = request.POST.get('page')
        if page == 'start':
            page = '1'
        elif page == 'end':
            page = page_numbers
    try:
        comment_page = paginator.page(page)
    except PageNotAnInteger:
        comment_page = paginator.page(1)
    except EmptyPage:
        comment_page = paginator.page(paginator.num_pages)
    return render(request, 'backend/comment_manage.html', {
        'comment_page': comment_page,
        'page_numbers': page_numbers,
        'request_method': request_method,
        'searcharticle': searcharticle,
        'searchcontent': searchcontent,
        'published_date': pubdate,
    })

@login_required
def comment_update_status(request):
    '''评论状态更新'''
    if request.POST.get('type') == u'update_comment':
        '''更新评论的状态'''
        for comment in request.POST.getlist(u'obj_lists[]'):
            comment_obj = frontend_models.Comments.objects.get(pk=comment)
            if comment_obj.status:
                comment_obj.status = False
            else:
                comment_obj.status = True
            comment_obj.save()
        return HttpResponse("更新成功!")

@login_required
def categories_manage(request):
    '''博文分类管理'''
    if request.method == 'GET':
        '''GET方法处理页面返回'''
        categories = frontend_models.Categories.objects.all()
        if request.GET.get('cate_id'):
            '''带要修改的分类返回'''
            cate_change = frontend_models.Categories.objects.get(pk=request.GET.get('cate_id'))
            return render(request, 'backend/categories_manage.html', {'categories': categories, 'cate_change': cate_change})
        else:
            '''普通返回'''
            return render(request, 'backend/categories_manage.html', {'categories': categories})
    elif request.method == 'POST':
        '''负责内容提交'''
        if request.POST.get('type') == 'update_cate':
            '''通过type判断是更新状态还是提交内容,这里表示更新状态'''
            for cate in request.POST.getlist('obj_lists[]'):
                cate_obj = frontend_models.Categories.objects.get(pk=cate)
                if cate_obj.status:
                    cate_obj.status = False
                else:
                    cate_obj.status = True
                cate_obj.save()
            return HttpResponse("更新成功!")
        if request.POST.get('type') == 'create_cate':
            '''这里为提交内容'''
            if request.POST.get('commit_type') == 'create':
                '''提交内容中的commit_type为提交类型,create为创建一个新的分类,update为更新一个已有的分类'''
                new_cate = frontend_models.Categories(name=request.POST['catename'],
                                                       url=request.POST['cateurl'],
                                                      type=request.POST['catetype'])
                new_cate.save()
                return HttpResponse(u"%s , 创建成功!" % new_cate.name)
            elif request.POST.get('commit_type') == 'update':
                '''更新已有分类'''
                old_cate = frontend_models.Categories.objects.get(pk=request.POST.get('cate_id'))
                old_cate.name=request.POST['catename']
                old_cate.url=request.POST['cateurl']
                old_cate.type=request.POST['catetype']
                old_cate.save()
                return HttpResponse(u"%s , 更新成功!" % old_cate.name)

@login_required
def load(request):
    '''CPU Load'''
    time_condition = timezone.localtime(timezone.now() - timezone.timedelta(days=3))
    cpuload_list = backend_models.Cpuload.objects.filter(timestamp__gt=time_condition)
    data = {'oneminutes': [], 'fiveminutes': [], 'fifteenminutes': []}
    for obj in cpuload_list:
        data['oneminutes'].append({'name': obj.timestamp.strftime("%Y-%m-%d %T"), 'value': [obj.timestamp.strftime("%Y-%m-%d %T"), obj.oneminutes.to_eng_string()]})
        data['fiveminutes'].append({'name': obj.timestamp.strftime("%Y-%m-%d %T"), 'value': [obj.timestamp.strftime("%Y-%m-%d %T"), obj.fiveminutes.to_eng_string()]})
        data['fifteenminutes'].append({'name': obj.timestamp.strftime("%Y-%m-%d %T"), 'value': [obj.timestamp.strftime("%Y-%m-%d %T"), obj.fifteenminutes.to_eng_string()]})
    return HttpResponse(json.dumps(data))
