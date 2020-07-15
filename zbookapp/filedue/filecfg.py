import hashlib

from django.shortcuts import  HttpResponse
from django.db import connection
import json
from zbookapp import public
from zbookapp import models
import datetime
import os
import base64
import openpyxl
import zipfile


#文件处理
def admin(request):
    log = public.logger
    log.info('----------------------filecfg_begin---------------------------')

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

    log.info('----------------------filecfg_end---------------------------')
    return resp

#文件资源上传，反回md5值的url服务器路径
def file_upload(request, request_body):
    log = public.logger
    log.info('----------------------Admin-files_upload-begin---------------------------')
    filename=request_body.get('filename',None)
    username = request_body.get('username', None)
    file = request_body.get('file', None)
    name_id = request_body.get('name_id',0)
    uid = request_body.get('uid',None)

    if filename==None or len(filename)<2:
        s = public.setrespinfo({"respcode": "300001", "respmsg": "上送文件名错误"})
        return s
    if file==None:
        s = public.setrespinfo({"respcode": "300002", "respmsg": "上送文件内容错误"})
        return s
    if not username and not uid:
        s = public.setrespinfo({"respcode": "300003", "respmsg": "请登录！"})
        return s
    elif not uid:
        sql = "select user_id from zbookapp_user where username=%s"
        cur = connection.cursor()
        cur.execute(sql,username)
        row = cur.fetchone()
        cur.close()
        if row:
            uid = row[0]
        else:
            s = public.setrespinfo({"respcode": "300004", "respmsg": "用户不存在！"})
            return s
    print('file=',file)
    filename_ext=filename.split('.')[1]
    #生成md5值的文件名
    m2=hashlib.md5()
    m2.update(file.encode('raw_unicode_escape'))
    md5_filename=m2.hexdigest()+'.'+filename_ext

    # 保存文件到本地文件上传目录
    filepath=public.localhome+'fileup/'
    file_name = open(filepath+md5_filename, 'wb')
    mylen = len(request_body['file'])
    log.info('mylen=' + str(mylen))
    file_name.write(file.encode('raw_unicode_escape')) #前端在json报文中，把二进制当字符串上送了，可以这样转换
    file_name.close()


    #插入数据库
    cur = connection.cursor()
    sql = "insert into zbookapp_bookfile(file_id,user_id,file_name,md5_name,tran_date,status,name) value(%s,%s,%s,%s,%s,%s,%s)"
    res=cur.execute(sql, (None,uid,filename,md5_filename,datetime.datetime.now(),0,name_id))
    fileid=cur.lastrowid
    cur.close()
    data = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
        "fileid":str(fileid),
        'filename':filename
    }

    s = json.dumps(data, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-files_upload-end---------------------------')
    return HttpResponse(s)