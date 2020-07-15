from django.shortcuts import  HttpResponse
from django.db import connection
import json
from zbookapp import public
from zbookapp import models
import datetime
import hashlib,base64,re
import os
import time

# 个人信息处理
def admin(request):
    log = public.logger
    log.info('----------------------appreadact_begin---------------------------')

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

    log.info('----------------------appreadact_end---------------------------')
    return resp

#加入收藏
def joincol(request, request_body):
    log = public.logger
    log.info('----------------------Admin-getbookinfo-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
    }
    fileid = request_body.get('fileid', None)
    uid = request_body.get('userid', None)
    coltext='收藏'

    if uid:
        sql = "select * from zbookapp_user where user_id=%s"
        cur = connection.cursor()
        cur.execute(sql,uid)
        row = cur.fetchone()
        cur.close()
        if not row:
            s = public.setrespinfo({"respcode": "300004", "respmsg": "用户不存在！"})
            return s
    else:
        s = public.setrespinfo({"respcode": "300003", "respmsg": "请登录！"})
        return s
    select_sql = "select * from zbookapp_collection where file_id=%s and user_id=%s and status='0' "
    cur = connection.cursor()
    cur.execute(select_sql,(fileid,uid))
    row = cur.fetchone()
    if row:
        s = public.setrespinfo({"respcode": "300006", "respmsg": "已加入收藏!"})
        return s
    try:
        join_sql = "INSERT INTO zbookapp_collection (file_id, user_id, tran_date, status) VALUES (%s, %s, %s, %s)"
        cur = connection.cursor()
        cur.execute(join_sql, (fileid,uid,datetime.datetime.now(),'0'))
        cur.close()
        coltext = '已收藏'
    except Exception as e:
        print(e)

    jsondata['coltext'] = coltext
    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-getbookinfo-end---------------------------')
    return HttpResponse(s)


# 个人信息修改保存
def updUserinfo(request, request_body):
    log = public.logger
    log.info('----------------------Admin-updUserinfo-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "保存成功",
        "trantype": request_body.get('trantype', None),
    }
    uid = request_body.get('userid', None)
    userinfo = request_body.get('userinfo', None)
    print(uid)
    if uid:
        sql = "select * from zbookapp_user where user_id=%s"
        cur = connection.cursor()
        cur.execute(sql, uid)
        row = cur.fetchone()
        cur.close()
        if not row:
            s = public.setrespinfo({"respcode": "300004", "respmsg": "用户不存在！"})
            return s
    else:
        s = public.setrespinfo({"respcode": "300003", "respmsg": "请登录！"})
        return s
    path = None
    if userinfo['userprofile']:
        print('url=',userinfo['userprofile'][0].get('url', None))
        if not userinfo['userprofile'][0].get('url',None):
            filename = userinfo['userprofile'][0]['name']
            file = userinfo['userprofile'][0]['content']
            print(filename,file)
            path = saveimg(filename,file)
        else:
            url = userinfo['userprofile'][0].get('url',None)
            filename = url.split('/')[-1]
            path = 'userpro/'+filename
    upd_sql = "UPDATE zbookapp_user SET userprofile=%s, nickname=%s, sex=%s, location=%s, email=%s, signature=%s, upd_date=%s WHERE user_id=%s "
    if userinfo:
        sexdict = {
            '男': 0,
            '女': 1,
            '未知': 2
        }
        sex = sexdict[userinfo['sex']]
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tuple = (path,userinfo['nickname'],sex,userinfo['location'],userinfo['email'],userinfo['signature'],nowTime,uid)
        print('tuple=',tuple)
        cur = connection.cursor()
        cur.execute(upd_sql, tuple)
        connection.commit()
        cur.close()
    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-updUserinfo-end---------------------------')
    return HttpResponse(s)

# 文档上传
# INSERT INTO zbookapp_bookfile(user_id, file_name, md5_name, tran_date, status, msg, name) VALUES (%s, %s, %s, %s, %s, %s, %s);
def handdoc(request, request_body):
    log = public.logger
    log.info('----------------------Admin-handdoc-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
    }
    uid = request_body.get('userid', None)
    filename = request_body.get('filename', None)
    file = request_body.get('file', None)
    classvalue = request_body.get('classvalue', None)
    contentinfo = request_body.get('contentinfo', None)
    share = request_body.get('share', None)

    solts_dict = {}
    # 查询分类列表
    solts_sql = "select * from zbookapp_soltslist"
    cur = connection.cursor()
    cur.execute(solts_sql)
    rows = cur.fetchall()
    for item in rows:
        solts_dict[item[1]] = item[0]
    if share:
        share = 1
    else:
        share = 0
    if classvalue:
        classvalue = solts_dict[classvalue]
    if uid:
        sql = "select * from zbookapp_user where user_id=%s"
        cur = connection.cursor()
        cur.execute(sql, uid)
        row = cur.fetchone()
        cur.close()
        if not row:
            s = public.setrespinfo({"respcode": "300004", "respmsg": "用户不存在！"})
            return s
    else:
        s = public.setrespinfo({"respcode": "300003", "respmsg": "请登录！"})
        return s

    if file:
        md5_filename = savedoc(filename,file)
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO zbookapp_bookfile(user_id, file_name, md5_name, tran_date, status, msg, name) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cur = connection.cursor()
        tuple = (uid,filename,md5_filename,nowTime,share,contentinfo,classvalue)
        cur.execute(sql,tuple)
        cur.close()


    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-handdoc-end---------------------------')
    return HttpResponse(s)

# 保存图片
def saveimg(filename,file):
    filename_ext = filename.split('.')[1]
    # 1、信息提取
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", file, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")

    else:
        raise Exception("Do not parse!")
    # 2、base64解码
    file = base64.urlsafe_b64decode(data)

    # 生成md5值的文件名
    m2 = hashlib.md5()
    # m2.update(file.encode('raw_unicode_escape'))
    m2.update(file)
    md5_filename = m2.hexdigest() + '.' + filename_ext

    # 保存文件到本地文件上传目录
    filepath = public.localhome + 'media/userpro/'
    file_name = open(filepath + md5_filename, 'wb')
    file_name.write(file)  # 前端在json报文中，把二进制当字符串上送了，可以这样转换
    file_name.close()
    path = 'userpro/'+md5_filename
    return path

# 保存文档
def savedoc(filename,file):
    filename_ext = filename.split('.')[1]
    # 生成md5值的文件名
    m2 = hashlib.md5()
    m2.update(file.encode('raw_unicode_escape'))
    md5_filename = m2.hexdigest() + '.' + filename_ext

    # 保存文件到本地文件上传目录
    filepath = public.localhome + 'fileup/'
    file_name = open(filepath + md5_filename, 'wb')
    file_name.write(file.encode('raw_unicode_escape'))  # 前端在json报文中，把二进制当字符串上送了，可以这样转换
    file_name.close()

    return md5_filename