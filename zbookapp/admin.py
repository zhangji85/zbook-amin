from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe
from django.conf.global_settings import MEDIA_URL

# Register your models here.
admin.site.site_header = 'ZBOOK管理后台'
admin.site.site_title = 'ZBOOK智阅网'

#用户列表注册
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id','username','password','image_data','nickname','sex','location','email','signature','upd_date','tran_date','status')
    # list_editable 设置默认可编辑字段，在列表里就可以编辑
    list_editable = ['sex','status']
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20
    # 设置哪些字段可以点击进入编辑界面
    list_display_links = ('user_id','username','image_data','password','nickname')
    # 操作选项列表顶部，设置为False不在顶部显示，默认为True。
    actions_on_top = False
    # 操作选项列表底部，设置为False不在底部显示，默认为False。
    actions_on_bottom = True
    #指定搜索字段
    search_fields = ['username','sex','tran_date']
    # 右侧栏过滤器，按状态进行筛选
    list_filter = ['status']
    readonly_fields = ('image_data','location','email')


@admin.register(BookShelf)
class BookShelfAdmin(admin.ModelAdmin):
    list_display = ('user_id','file_id','tran_date','upd_date','status')
    # list_editable 设置默认可编辑字段，在列表里就可以编辑
    list_editable = ['status']
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20
    # 设置哪些字段可以点击进入编辑界面
    list_display_links = ('file_id', 'user_id')
    # 操作选项列表顶部，设置为False不在顶部显示，默认为True。
    actions_on_top = False
    # 操作选项列表底部，设置为False不在底部显示，默认为False。
    actions_on_bottom = True
    # 指定搜索字段
    search_fields = ['user_id', 'file_id', 'tran_date','upd_date','status']
    # 右侧栏过滤器，按状态进行筛选
    list_filter = ['status']


@admin.register(Bookfile)
class BookfileAdmin(admin.ModelAdmin):
    list_display = ('file_id','user_id','file_name','solts','tran_date','status')
    # list_editable 设置默认可编辑字段，在列表里就可以编辑
    list_editable = ['status']
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20
    # 设置哪些字段可以点击进入编辑界面
    list_display_links = ('file_id', 'user_id', 'file_name','solts')
    # 操作选项列表顶部，设置为False不在顶部显示，默认为True。
    actions_on_top = False
    # 操作选项列表底部，设置为False不在底部显示，默认为False。
    actions_on_bottom = True
    # 指定搜索字段
    search_fields = ['user_id', 'file_name', 'solts','status']
    # 右侧栏过滤器，按状态进行筛选
    list_filter = ['solts','status']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('file_id','user_id','tran_date','status')
    # list_editable 设置默认可编辑字段，在列表里就可以编辑
    list_editable = ['status']
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20
    # 设置哪些字段可以点击进入编辑界面
    list_display_links = ('file_id', 'user_id')
    # 操作选项列表顶部，设置为False不在顶部显示，默认为True。
    actions_on_top = False
    # 操作选项列表底部，设置为False不在底部显示，默认为False。
    actions_on_bottom = True
    # 指定搜索字段
    search_fields = ['user_id','status']
    # 右侧栏过滤器，按状态进行筛选
    list_filter = ['tran_date','status']

@admin.register(Soltslist)
class SoltslistAdmin(admin.ModelAdmin):
    list_display = ['name']
    # # list_editable 设置默认可编辑字段，在列表里就可以编辑
    # list_editable = ['name']
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20
    # 设置哪些字段可以点击进入编辑界面
    list_display_links = ['name']
    # 操作选项列表顶部，设置为False不在顶部显示，默认为True。
    actions_on_top = False
    # 操作选项列表底部，设置为False不在底部显示，默认为False。
    actions_on_bottom = True
    # 指定搜索字段
    search_fields = ['name']