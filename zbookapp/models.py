from django.db import models
import json
from datetime import datetime,date
import decimal
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.conf.global_settings import MEDIA_ROOT

# Create your models here.

# 用户信息表
class User(models.Model):
    user_id = models.AutoField(primary_key=True,verbose_name='用户ID')
    username=models.CharField(max_length=20,verbose_name='用户名')
    password=models.CharField(max_length=32,verbose_name='密码')
    userprofile = models.ImageField(blank=True, null=True,upload_to='userpro',verbose_name='头像',default='userpro/default.jpg')
    nickname = models.CharField(max_length=32, blank=True, null=True,verbose_name='昵称')
    sex_status = ((0, u'男'), (1, u'女'), (2, u'未知'))
    sex = models.IntegerField(choices=sex_status, verbose_name='性别', default=2)
    location = models.CharField(max_length=30, blank=True, null=True,verbose_name='地区')
    email=models.CharField(max_length=30,blank=True,verbose_name='邮箱',null=True)
    signature = models.CharField(max_length=100, blank=True, null=True,verbose_name='个性签名')
    upd_date = models.DateTimeField(auto_now=True,null=True,verbose_name='更新时间')
    tran_date = models.DateTimeField(auto_now_add=True,verbose_name='注册时间')
    status_type = ((0, u'正常'), (1, u'禁用'))
    status=models.IntegerField(choices=status_type,verbose_name='状态',default=0)#0正常 1禁用

    def image_data(self):
        if self.userprofile:
            return format_html(
                '<img src="{}" width="80px"/>',
                self.userprofile.url)
        else:
            return ('-')

    image_data.short_description = u'头像'

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户列表'

#  书架
class BookShelf(models.Model):
    user_id = models.IntegerField(verbose_name='用户ID')
    file_id = models.IntegerField(verbose_name='文档ID')
    tran_date = models.DateTimeField(auto_now_add=True,verbose_name='插入时间')
    upd_date = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    bookshelf_status = ((0, u'正常'), (1, u'已移出'))
    status = models.IntegerField(choices=bookshelf_status,verbose_name='状态',default=0)

    class Meta:
        verbose_name = u'书架'
        verbose_name_plural = u'书架管理'
        managed = False
        db_table = 'book_shelf'

# 书籍分类
class Soltslist(models.Model):
    name = models.CharField(max_length=100,unique=True,verbose_name='类别')
    class Meta:
        verbose_name = u'类别'
        verbose_name_plural = u'文档类别'
    def __str__(self):
        return self.name

# 用户上传书籍列表
class Bookfile(models.Model):
    file_id = models.AutoField(primary_key=True, verbose_name='文件ID')
    user_id=models.IntegerField(verbose_name='用户ID')
    file_name=models.CharField(max_length=50,verbose_name='文件名')
    md5_name=models.CharField(max_length=50,verbose_name='md5文件名')
    solts =  models.ForeignKey('Soltslist',db_column='name',on_delete=models.CASCADE,verbose_name='所属分类',null=True)
    tran_date = models.DateTimeField(auto_now_add=True,verbose_name='上传时间')
    status_type = ((0, u'私有'), (1, u'共享'),(-1, u'已移除'))
    status=models.IntegerField(choices=status_type,verbose_name='状态',default=0)
    class Meta:
        verbose_name = u'文件'
        verbose_name_plural = u'文档管理'

# 用户收藏列表
class Collection(models.Model):
    file_id = models.IntegerField(verbose_name='文件ID')
    user_id=models.IntegerField(verbose_name='用户ID')
    tran_date = models.DateTimeField(auto_now_add=True,verbose_name='收藏时间')
    status_type = ((0, u'正常'), (1, u'已移出'))
    status=models.IntegerField(choices=status_type,verbose_name='状态',default=0)#0正常 1禁用
    class Meta:
        verbose_name = u'收藏'
        verbose_name_plural = u'收藏列表'

#将date datetime decimal类型转换为json
class JsonCustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o,decimal.Decimal):
            return float(o)
        else:
            return json.JSONEncoder.default(self, o)
