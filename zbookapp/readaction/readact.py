from django.shortcuts import  HttpResponse
from django.db import connection
import json
from zbookapp import public
from zbookapp import models
from zbookapp.createanswer.Answermatch.matchfun.QAFun import alloperate
import datetime
import os
import time



#阅读处理
def admin(request):
    log = public.logger
    log.info('----------------------readact_begin---------------------------')

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

    log.info('----------------------readact_end---------------------------')
    return resp

#文件列表
def getfilelist(request, request_body):
    log = public.logger
    log.info('----------------------Admin-getfilelist-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "上传成功",
        "trantype": request_body.get('trantype', None),
    }

    username = request_body.get('username', None)
    uid = ''

    if username==None:
        s = public.setrespinfo({"respcode": "300003", "respmsg": "请登录！"})
        return s
    else:
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

    solts_dict = {}
    # 查询分类列表
    solts_sql = "select * from zbookapp_soltslist"
    cur = connection.cursor()
    cur.execute(solts_sql)
    rows = cur.fetchall()
    for item in rows:
        solts_dict[item[0]] = item[1]

    fileoptions = []
    upfile_dict = {'value': 'myupload',
                    'label': '我的上传',
                   'children':[]}
    # 查询我的上传
    uplist_sql = "select * from zbookapp_bookfile where user_id=%s and name=%s and status!= -1 "
    soltnum_sql = "select name from zbookapp_bookfile where user_id = %s and status!= -1 group by name"
    cur = connection.cursor()
    cur.execute(soltnum_sql,uid)
    solts1_rows = cur.fetchall()
    if solts1_rows:
        for item in solts1_rows:
            tmp_dict = {
                'value': item[0],
                'label': solts_dict[item[0]],
                'children': []
            }
            cur.execute(uplist_sql,(uid,item[0]))
            file_rows = cur.fetchall()
            if file_rows:
                for file in file_rows:
                    tmp = {
                        'value': file[0],
                        'label': file[2],
                    }
                    tmp_dict['children'].append(tmp)
            upfile_dict['children'].append(tmp_dict)
    fileoptions.append(upfile_dict)

    # 查询我的收藏
    collfile_dict = {'value': 'mycollection',
                   'label': '我的收藏',
                   'children': []}
    collist_sql = "select file_id from zbookapp_collection where user_id=%s and status= 0 "
    file_sql = "select * from zbookapp_bookfile where file_id = %s and status=1"
    cur = connection.cursor()
    cur.execute(collist_sql, uid)
    coll_rows = cur.fetchall()
    if coll_rows:
        tmp_list_dict = {}
        for item in solts_dict.keys():
            tmp_list_dict[item] = []
        for item in coll_rows:
            cur.execute(file_sql, (item[0]))
            file_row = cur.fetchone()
            if file_row:
                tmp = {
                    'value': file_row[0],
                    'label': file_row[2],
                }
                tmp_list_dict[file_row[-1]].append(tmp)
        for item in tmp_list_dict.keys():
            if len(tmp_list_dict[item])!=0:
                child_dict = {
                    'value': item,
                    'label': solts_dict[item],
                    'children': tmp_list_dict[item]
                }
                collfile_dict['children'].append(child_dict)
    fileoptions.append(collfile_dict)
    jsondata['fileoptions'] = fileoptions

    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-getfilelist-end---------------------------')
    return HttpResponse(s)

# 智能阅读处理
def create_answer(request, request_body):
    log = public.logger
    log.info('----------------------Admin-create_answer-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "处理完成",
        "trantype": request_body.get('trantype', None),
    }

    question = request_body.get('question', None)
    filelist = request_body.get('filelist', None)
    if filelist:
        fileid = filelist[-1]
    else:
        s = public.setrespinfo({"respcode": "400001", "respmsg": "文件不存在！"})
        return s
    if len(question)==0:
        s = public.setrespinfo({"respcode": "400002", "respmsg": "请输入问题！"})
        return s
    # 查询文件信息
    file_sql = "select * from zbookapp_bookfile where file_id = %s "
    cur = connection.cursor()
    cur.execute(file_sql, fileid)
    row = cur.fetchone()
    if row:
        md5_filename = row[3]
        md5file = md5_filename.split('.')[0]
        data_path = public.localhome + "fileup//"+md5_filename
        tmp_answer = []
        try:
            tmp_answer = alloperate(md5file,data_path,question)
        except Exception as e:
            print('e=',e)
        answer = []
        if tmp_answer:
            for item in tmp_answer:
                tmp_lineid = str(item['line_id'])
                item['line_id'] = tmp_lineid
                answer.append(item)
        jsondata['answerlist'] = answer
    else:
        s = public.setrespinfo({"respcode": "400001", "respmsg": "文件不存在！"})
        return s



    s = json.dumps(jsondata, cls=models.JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-create_answer-end---------------------------')
    return HttpResponse(s)