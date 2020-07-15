from django.shortcuts import  HttpResponse
from django.db import connection
import json
from zbookapp import public
from zbookapp import models
from zbookapp.createanswer.Answermatch.matchfun.QAFun import alloperate
import datetime
import os
import time



#页面展示
def admin(request):
    log = public.logger
    log.info('----------------------appview_begin---------------------------')

    if request.method == "POST":
        # #请求body转为json
        tmp=request.body
        tmp=tmp.decode(encoding='utf-8')
        request_body=json.loads(tmp)
        trantype = request_body['trantype']
        log.info('trantype=[%s]' % trantype)
        fun_name = trantype
        if globals().get(fun_name):
            resp = globals()[fun_name](request, request_body)
        else:
            s = public.setrespinfo({"respcode": "100000", "respmsg": "api error"})
            resp = HttpResponse(s)

    elif request.method == "GET":
        s = public.setrespinfo({"respcode": "000000", "respmsg": "api error"})
        resp = HttpResponse(s)

    log.info('----------------------appview_end---------------------------')
    return resp

#用户页面信息
def getuserpage(request, request_body):
    log = public.logger
    log.info('----------------------Admin-getuserpage-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
    }
    uid = request_body.get('userid', None)
    userprofile = ''
    username = ''
    if uid:
        sql = "select * from zbookapp_user where user_id=%s"
        cur = connection.cursor()
        cur.execute(sql,uid)
        row = cur.fetchone()
        cur.close()
        if not row:
            s = public.setrespinfo({"respcode": "300004", "respmsg": "用户不存在！"})
            return s
    try:
        username, basicinfo,userprofile = userpage(uid)
    except Exception as e:
        print('e=', e)
    jsondata['username'] = username
    jsondata['basicinfo'] = basicinfo
    jsondata['userprofile'] = userprofile
    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-getuserpage-end---------------------------')
    return HttpResponse(s)

# 个人信息
def getuserinfo(request, request_body):
    log = public.logger
    log.info('----------------------Admin-getuserpage-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
    }
    uid = request_body.get('userid', None)

    userinfo = {
        'userid': uid,
        'username': '', # 用户名
        'userprofile': [], # 头像
        'nickname': '张先生', # 昵称
        'sex': '男', # 性别
        'location': '', # 地区
        'email': '', # email
        'signature': '听闻小姐治家有方，余生愿闻其详。' # 个性签名
    }
    sexdict = {
        0:'男',
        1:'女',
        2:'未知'
    }
    userprofile = ''
    if uid:
        sql = "select * from zbookapp_user where user_id=%s"
        cur = connection.cursor()
        cur.execute(sql,uid)
        row = cur.fetchone()
        cur.close()
        if row:
            userprofile = []
            if models.User.objects.get(user_id=uid).userprofile:
                userprofile = public.localurl+ models.User.objects.get(user_id=uid).userprofile.url
                userprofile = [{'url':userprofile}]
            userinfo = {
                'userid': row[0],
                'username': row[1],  # 用户名
                'userprofile': userprofile,  # 头像
                'nickname': row[4],  # 昵称
                'sex': sexdict[row[5]],  # 性别
                'location': row[6],  # 地区
                'email': row[7],  # email
                'signature': row[8]  # 个性签名
            }
            for key in userinfo.keys():
                if not userinfo[key]:
                    userinfo[key] = ''
        else:
            s = public.setrespinfo({"respcode": "300004", "respmsg": "用户不存在！"})
            return s

    jsondata['userinfo'] = userinfo
    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-getuserpage-end---------------------------')
    return HttpResponse(s)

#文件列表
def getlist(request, request_body):
    log = public.logger
    log.info('----------------------Admin-getfilelist-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
    }
    uid = request_body.get('userid', None)
    condition = request_body.get('condition', None)

    if uid and uid!='share':
        sql = "select * from zbookapp_user where user_id=%s"
        cur = connection.cursor()
        cur.execute(sql,uid)
        row = cur.fetchone()
        cur.close()
        if not row:
            s = public.setrespinfo({"respcode": "300004", "respmsg": "用户不存在！"})
            return s
    solts_dict = {}
    # 查询分类列表
    solts_sql = "select * from zbookapp_soltslist"
    cur = connection.cursor()
    cur.execute(solts_sql)
    rows = cur.fetchall()
    condition_id = None
    for item in rows:
        if condition == item[1]:
            condition_id = item[0]
        solts_dict[item[0]] = item[1]
    file_list = []

    # condition_id 不为空，为分类菜单列表
    print('condition=',condition,condition_id)
    if condition_id!=None:
        file_list = conditionList(condition_id)
    else:
        if condition=='推荐':
            file_list = Tjlist(solts_dict)
        elif condition == '最新':
            file_list = Zxlist(solts_dict)
        elif condition == '我的上传':
            if uid:
                file_list = handlist(uid,solts_dict)
            else:
                s = public.setrespinfo({"respcode": "300003", "respmsg": "请登录！"})
                return s
        elif condition == '我的收藏':
            if uid:
                file_list = collist(uid, solts_dict)
            else:
                s = public.setrespinfo({"respcode": "300003", "respmsg": "请登录！"})
                return s
        elif condition == '书架':
            print('uid=',uid)
            if uid:
                file_list = shelfist(uid)
            else:
                s = public.setrespinfo({"respcode": "300003", "respmsg": "请登录！"})
                return s

    jsondata['list'] = file_list
    print('file_list=',file_list)
    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-getfilelist-end---------------------------')
    return HttpResponse(s)

#书籍详情
def getbookinfo(request, request_body):
    log = public.logger
    log.info('----------------------Admin-getbookinfo-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
    }
    uid = request_body.get('userid', None)
    fileid = request_body.get('fileid', None)

    filename=''
    fileinfo=''
    shelftext=''
    coltext=''

    if uid:
        sql = "select * from zbookapp_user where user_id=%s"
        cur = connection.cursor()
        cur.execute(sql, uid)
        row = cur.fetchone()
        cur.close()
        if not row:
            s = public.setrespinfo({"respcode": "300004", "respmsg": "用户不存在！"})
            return s
    file_sql = "select * from zbookapp_bookfile where file_id=%s "
    cur = connection.cursor()
    cur.execute(file_sql, fileid)
    row = cur.fetchone()
    if row:
        filename = row[2]
        fileinfo = row[-2]
    if uid:
        col_sql = "select * from zbookapp_collection where user_id = %s and file_id=%s and status= 0 "
        shelf_sql = "select * from book_shelf where user_id = %s and file_id=%s and status= 0"
        cur.execute(col_sql,(uid,fileid))
        row = cur.fetchone()
        if row:
            coltext = '已收藏'
        else:
            coltext = '收藏'

        cur.execute(shelf_sql, (uid, fileid))
        row = cur.fetchone()
        if row:
            shelftext = '已加入书架'
        else:
            shelftext = '加入书架'
    else:
        coltext = '收藏'
        shelftext = '加入书架'

    jsondata['filename'] = filename
    jsondata['fileinfo'] = fileinfo
    jsondata['coltext'] = coltext
    jsondata['shelftext'] = shelftext
    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-getbookinfo-end---------------------------')
    return HttpResponse(s)

# 共享页面信息
def getSharelist(request, request_body):
    log = public.logger
    log.info('----------------------Admin-getSharelist-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
    }

    solts_dict = {}
    # 查询分类列表
    solts_sql = "select * from zbookapp_soltslist"
    cur = connection.cursor()
    cur.execute(solts_sql)
    rows = cur.fetchall()
    condition_id = None
    conditionid_list = []
    for item in rows:
        solts_dict[item[0]] = item[1]
        conditionid_list.append(item[0])

    alllist = []
    for id in conditionid_list:
        sql = "select * from zbookapp_bookfile where status=1 and name=%s "
        cur.execute(sql,id)
        rows = cur.fetchall()
        if rows:
            tmp_dict = {'condition_id': id, 'name': solts_dict[id]}
            tmp_list = []
            for row in rows:
                colnum_sql = "select COUNT(*) as num from zbookapp_collection where file_id=%s and status= 0 "
                cur.execute(colnum_sql, row[0])
                colnum = cur.fetchone()[0]
                item_dict = {
                    'filename': row[2],
                    'fileid': row[0],
                    'msg': row[-2],
                    'colnum': colnum
                }
                tmp_list.append(item_dict)
            tmp_dict['list'] = tmp_list
            alllist.append(tmp_dict)
    jsondata['alllist'] = alllist
    print('alllist=',alllist)
    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-getSharelist-end---------------------------')
    return HttpResponse(s)

# 推荐列表
def Tjlist(solts_dict):
    tjlist_sql = "select * from zbookapp_bookfile where file_id=%s and status= 1 "
    tjlist_else_sql = "select * from zbookapp_bookfile where status= 1"
    fileid_list_sql = "select file_id,COUNT(file_id) as num from zbookapp_collection where status= 0 " \
                      "GROUP BY file_id order by num desc"

    tjlist = []
    cur = connection.cursor()
    cur.execute(fileid_list_sql)
    rows = cur.fetchall()
    if rows:
        for item in rows:
            cur.execute(tjlist_sql,item[0])
            row = cur.fetchone()
            if row:
                tmp_dict = {
                    'filename':row[2],
                    'fileid':row[0],
                    'msg': row[-2],
                    'class':solts_dict[row[-1]],
                    'colnum':item[1]
                }
                tjlist.append(tmp_dict)
    else:
        cur.execute(tjlist_else_sql)
        row = cur.fetchone()
        if row:
            tmp_dict = {
                'filename': row[2],
                'fileid': row[0],
                'class': solts_dict[row[-1]],
                'colnum': 0,
                'msg':row[-2]
            }
            tjlist.append(tmp_dict)

    return tjlist

# 最新列表
def Zxlist(solts_dict):
    zxlist_sql = "select * from zbookapp_bookfile where status= 1 order by tran_date desc "
    colnum_sql = "select COUNT(*) as num from zbookapp_collection where file_id=%s and status= 0 "

    zxlist = []
    cur = connection.cursor()
    cur.execute(zxlist_sql)
    rows = cur.fetchall()
    if rows:
        for item in rows:
            cur.execute(colnum_sql,item[0])
            row = cur.fetchone()
            colnum = 0
            if row:
               colnum = row[0]
            tmp_dict = {
                'filename':item[2],
                'fileid':item[0],
                'msg': item[-2],
                'class':solts_dict[item[-1]],
                'colnum':colnum
            }
            zxlist.append(tmp_dict)

    return zxlist

# 我的上传
def handlist(uid,solts_dict):
    # 查询我的上传
    uplist_sql = "select * from zbookapp_bookfile where user_id=%s and status!= -1"
    colnum_sql = "select COUNT(*) as num from zbookapp_collection where file_id=%s and status= 0 "
    handlist = []
    cur = connection.cursor()
    cur.execute(uplist_sql, uid)
    file_rows = cur.fetchall()
    if file_rows:
        for item in file_rows:
            cur.execute(colnum_sql, item[0])
            colnum = cur.fetchone()[0]
            if item[-3]==1:
                status = '已共享'
            else:
                status = '未共享'
            tmp_dict = {
                'filename': item[2],
                'fileid': item[0],
                'class': solts_dict[item[-1]],
                'colnum': colnum,
                'status':status,
            }
            handlist.append(tmp_dict)
    return handlist

# 我的收藏
def collist(uid,solts_dict):
    collist_sql = "select * from zbookapp_collection where user_id = %s and status= 0 order by tran_date desc "
    file_sql = "select * from zbookapp_bookfile where file_id=%s and status=1 "
    colnum_sql = "select COUNT(*) as num from zbookapp_collection where file_id=%s and status= 0 "

    collist = []
    cur = connection.cursor()
    cur.execute(collist_sql,uid)
    rows = cur.fetchall()
    if rows:
        for item in rows:
            cur.execute(file_sql,item[0])
            row = cur.fetchone()
            cur.execute(colnum_sql,item[0])
            colnum = cur.fetchone()[0]
            tmp_dict = {
                'filename':row[2],
                'fileid':row[0],
                'msg': row[-2],
                'class':solts_dict[row[-1]],
                'colnum':colnum,
                'trantype':'updcollstatus'
            }
            collist.append(tmp_dict)

    return collist

# 我的书架
def shelfist(uid):
    shelflist_sql = "select * from book_shelf where user_id = %s and status= 0 order by tran_date desc "
    file_sql = "select * from zbookapp_bookfile where file_id=%s "

    shelfist = []
    cur = connection.cursor()
    cur.execute(shelflist_sql,uid)
    rows = cur.fetchall()
    print('rows=',rows)
    if rows:
        for item in rows:
            cur.execute(file_sql,item[2])
            row = cur.fetchone()
            if row:
                tmp_dict = {
                    'id':row[0],
                    'filename':row[2],
                    'fileid':row[0],
                    'msg': row[-2]
                }
                shelfist.append(tmp_dict)
    print('shelfist=',shelfist)
    return shelfist

# 单个分类列表
def conditionList(condition_id):
    file_sql = "select * from zbookapp_bookfile where name=%s and status=1 "
    colnum_sql = "select COUNT(*) as num from zbookapp_collection where file_id=%s and status= 0 "
    print('lallalalal')
    list = []
    cur = connection.cursor()
    cur.execute(file_sql,condition_id)
    rows = cur.fetchall()
    print('rows=',rows)
    for row in rows:
        cur.execute(colnum_sql,row[0])
        colnum = cur.fetchone()[0]
        tmp_dict = {
            'filename':row[2],
            'fileid':row[0],
            'msg': row[-2],
            'colnum':colnum
        }
        list.append(tmp_dict)

    return list

# 获取用户的用户名
def userpage(uid):
    user_sql = "select * from zbookapp_user where user_id=%s"
    uptotal_sql = "select count(*) from zbookapp_bookfile where user_id=%s and status!= -1"
    colltotal_sql = "select count(*) from zbookapp_collection where user_id = %s and status= 0"
    shelftotal_sql = "select count(*) from book_shelf where user_id = %s and status= 0"
    basicinfo = [
        {
            "name":"上传",
            'value': '0'
        },
        {
            'name': '收藏',
            'value': '0',
        },
        {
            'name': '书架',
            'value': '0',
        },
    ]
    userprofile = []
    cur = connection.cursor()
    cur.execute(user_sql,uid)
    row = cur.fetchone()
    if row[4]:
        username = row[4]
    else:
        username = row[1]
    if models.User.objects.get(user_id=uid).userprofile:
        userprofile   = public.localurl+ models.User.objects.get(user_id=uid).userprofile.url
    try:
        cur.execute(uptotal_sql,uid)
        uptotal = cur.fetchone()
        if uptotal:
            basicinfo[0]['value'] = uptotal[0]
        else:
            basicinfo[0]['value'] = 0

        cur.execute(colltotal_sql,uid)
        colltotal = cur.fetchone()
        if colltotal:
            basicinfo[1]['value'] = colltotal[0]
        else:
            basicinfo[1]['value'] = 0

        cur.execute(shelftotal_sql,uid)
        shelftotal = cur.fetchone()
        if shelftotal:
            basicinfo[2]['value'] = shelftotal[0]
        else:
            basicinfo[2]['value'] = 0
    except Exception as e:
        print('ee',e)
    print('userprofile=',userprofile)

    return username,basicinfo,userprofile