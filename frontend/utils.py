#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import models
from ibash import settings
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, pytz, time, os, send_email
from django.utils.safestring import mark_safe

def json_date_handler(obj):
    '''json.dumps(obj, default=json_date_handler)可以将obj中的时间对象格式化成字符串'''
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d %T")

def ConvertTime(comment, timez):
    '''将数据库中存储的utc时间转换为本地时间'''
    localtz = pytz.timezone(timez)
    utctz = pytz.timezone('UTC')
    localtime = comment.published_date.replace(tzinfo=utctz).astimezone(localtz)
    return localtime

def recursion_comm(comment, comment_tree, timez):
    '''递归评论'''
    for comm_parent in comment_tree:
        if comment.parent_comment_id == comm_parent['id']:
            pub_date = ConvertTime(comment, timez)
            comm_parent['children'].append({'id': comment.id, 'pid': comment.parent_comment_id, 'comment': comment.comment, 'published_date': pub_date, 'nickname': comment.nickname, 'client_type': comment.client_type, 'children': []})
        else:
            recursion_comm(comment, comm_parent['children'], timez)

def handle_comm(comment_list, timez):
    '''构造树形的评论结构'''
    comment_tree = []
    for comment in comment_list:
        if comment.parent_comment_id is None:
            pub_date = ConvertTime(comment, timez)
            comment_tree.append({'id': comment.id, 'pid': 0, 'comment': comment.comment, 'published_date': pub_date, 'nickname': comment.nickname, 'client_type': comment.client_type, 'children': []})
        else:
            recursion_comm(comment, comment_tree, timez)
    return comment_tree

def handle_single_comm(comm, timez):
    '''前端提交评论之后,用于构造当个评论的数据,用于前端展示'''
    pub_date = ConvertTime(comm, timez)
    if comm.parent_comment_id is None:
        pid = 0
    else:
        pid = comm.parent_comment_id
    return {'id': comm.id, 'pid': pid, 'comment': comm.comment, 'published_date': pub_date, 'nickname': comm.nickname, 'client_type': comm.client_type, 'children': []}

class VerifyCode(object):
    '''生成验证码'''
    def __init__(self, nums):
        font_path = '%s/static/img/ARIAL.TTF' % settings.BASE_DIR# 字体存放路径
        self.nums = self.__str2num(nums)
        self.width = 60 * self.nums
        self.height = 60
        self.__image = Image.new('RGB', (self.width, self.height), (255, 255, 255))#新建画布
        self.__font = ImageFont.truetype(font_path, 36)#新建字体,要保证字体存在,
        self.__draw = ImageDraw.Draw(self.__image)#绘画对象
        self.__vcode = []
        self.name = ''
        self.code = ''

    def gencode(self):
        '''生成验证码'''
        codepath = settings.VCODE
        name = str(time.time()) + '.jpg'
        self.__bgimg()
        self.__Vcode()
        self.__image = self.__image.filter(ImageFilter.BLUR)
        self.__image.save('%s/%s' % (codepath, name), 'jpeg')
        vcode = ''.join(self.__vcode)
        v_obj = models.Vcode(vcodefilename=name, vcode=vcode)
        v_obj.save()
        return v_obj

    def __rndChar(self):
        '''随机字符'''
        ch = chr(random.randint(65, 90))
        self.__vcode.append(ch)
        return ch

    def __rndColor(self):
        '''随机颜色'''
        return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

    def __rndColor2(self):
        '''随机颜色2'''
        return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

    def __bgimg(self):
        '''填充背景'''
        for x in range(self.width):
            for y in range(self.height):
                self.__draw.point((x, y), fill=self.__rndColor())

    def __Vcode(self):
        '''填充验证码'''
        for t in range(self.nums):
            self.__draw.text((60 * t + 10, 10), self.__rndChar(), font=self.__font, fill=self.__rndColor2())


    def __str2num(self, nums):
        '''验证数字'''
        if isinstance(nums, int):
            return nums
        elif str(nums).isdigit(nums):
            return nums
        else:
            raise TypeError

class SaveComment(object):
    '''保存评论'''
    def __init__(self, request, article_id):
        self.__comment = request.POST['comment']
        self.__nickname = request.POST['nickname']
        self.__email = request.POST['email']
        self.__client_ip = request.environ['REMOTE_ADDR']
        self.__parent_comment_id = self.__handler_pid(request.POST['pid'])
        self.__article_id = article_id
        self.__client_type = self.__uagent(request.environ['HTTP_USER_AGENT'])

    def __uagent(self, useragent):
        if "Chrome" in useragent and "Safari" in useragent:
            return "Google Chrome"
        elif "Safari" in useragent and "iPhone" in useragent:
            return "iPhone Safari"
        elif "Safari" in useragent and "Macintosh" in useragent and "Intel" in useragent:
            return "Mac OS X Safari"
        elif "Firefox" in useragent:
            return "Mozilla FireFox"
        elif "MSIE" in useragent and "Windows":
            return "Windows IE"

    def __handler_pid(self, pid):
        return None if pid == '0' else str(pid)

    def __send_mail(self):
        '''邮件发送提醒功能'''
        if self.__parent_comment_id is not None:
            p_obj = models.Comments.objects.get(pk=self.__parent_comment_id)
            if int(p_obj.article.id) == int(self.__article_id):
                reply_content = u'亲爱的<%s>同学:\n     有人回复了您的评论.http://ibash.cc/frontend/article/%s\n\niBash网站http://ibash.cc' % (p_obj.nickname, self.__article_id)
                reply_subject = u'<%s> 有人回复了您的评论----iBash网站' % p_obj.nickname
                reply_email_obj = send_email.Email(p_obj.nickname, p_obj.email)
                reply_email_obj.Send(reply_content, reply_subject)
        content = u'亲爱的<%s>同学:\n     感谢您的评论.http://ibash.cc/frontend/article/%s\n\niBash网站http://ibash.cc' % (self.__nickname, self.__article_id)
        subject = u'<%s> 感谢您的评论----iBash网站' % self.__nickname
        email_obj = send_email.Email(self.__nickname, self.__email)
        email_obj.Send(content, subject)

    def create(self):
        comment_obj = models.Comments(
            nickname=self.__nickname,
            email=self.__email,
            client_ip=self.__client_ip,
            client_type=self.__client_type,
            comment=self.__comment,
            article=models.ArticleInfo.objects.get(pk=self.__article_id),
            parent_comment_id=self.__parent_comment_id,
        )
        comment_obj.save()
        self.__send_mail()
        return comment_obj

class PageInfo(object):
    '''
        用来计算页数
        current_page当前页数
        all_count数据库中所有的记录数
        per_item每页显示多少记录
    '''
    def __init__(self, current_page, all_count, per_item=8):
        self.Current_page=current_page
        self.AllCount=all_count
        self.PerItem=per_item

    @property
    def start(self):
        return (self.Current_page-1)*self.PerItem

    @property
    def end(self):
        return self.Current_page*self.PerItem

    @property
    def all_page(self):
        all_page = divmod(self.AllCount, self.PerItem)
        if all_page[1] == 0:
            all_page=all_page[0]
        else:
            all_page=all_page[0] + 1
        # 末页bug(如果没人任何文章,点击末页会出现错误)
        if self.AllCount == 0:all_page = 1
        return all_page

def Pager(current_page, all_page):
    '''计算页数并拼接分页的字符串,current_page当前页码,all_page所有的页数'''
    page_html = []
    # 存放首页的字符串
    page_first='''<li><a href="?page=1" aria-label="Previous" target="_self"><span aria-hidden="true">首页</span></a></li>'''
    page_html.append(page_first)
    # 存放上一页
    if current_page <=1:
        page_prev='''<li class="disabled"><span aria-hidden="true">&lt;</span></li>'''
    else:
        page_prev='''<li><a href="?page=%d" target="_self">&lt;<span class="sr-only">(current)</span></a></li>''' % (current_page-1,)
    page_html.append(page_prev)
    # 显示的页码元素,建议显示奇数个页码,这里显示9个页码
    if all_page<9:
        begin_num=0
        end_num=all_page
    else:
        '''保证当前页码在最中间的位置'''
        if current_page<5:
            begin_num=0
            end_num=9
        else:
            if current_page + 4 > all_page:
                begin_num=current_page - 5
                end_num=all_page
            else:
                begin_num=current_page - 5
                end_num=current_page + 4
    for i in xrange(begin_num, end_num):
        if i + 1 == current_page:
            num_html='''<li class="active"><a href="?page=%d" target="_self">%d<span class="sr-only">(current)</span></a></li>''' %(i+1, i+1)
        else:
            num_html='''<li><a href="?page=%d" target="_self">%d<span class="sr-only">(current)</span></a></li>''' % (i + 1, i + 1)
        page_html.append(num_html)
    # 存放下一页
    if current_page < all_page:
        page_next='''<li><a href="?page=%d" target="_self" aria-label="Next"><span aria-hidden="true">&gt;</span></a></li>''' %(current_page+1,)
    else:
        page_next='''<li class="disabled"><span aria-hidden="true">&gt;</span></li>'''
    page_html.append(page_next)
    # 存放末页
    page_last='''<li><a href="?page=%d" target="_self" aria-label="Next"><span aria-hidden="true">末页</span></a></li>''' %(all_page)
    page_html.append(page_last)
    # 返回字符串
    page_string=mark_safe(''.join(page_html))
    return page_string