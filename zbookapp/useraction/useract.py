import hashlib
from django.shortcuts import  HttpResponse
from django.db import connection
import json
from zbookapp import public
# from zbookapp import models
import datetime
from zbookapp.models import *


#用户登录注册
def admin(request):
    log = public.logger
    log.info('----------------------useract_begin---------------------------')

    if request.method == "POST":
        # #请求body转为json
        tmp=request.body
        tmp=tmp.decode(encoding='utf-8')
        request_body=json.loads(tmp)
        trantype=request_body['trantype']
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

    log.info('----------------------useract_end---------------------------')
    return resp

# s = public.setrespinfo({"respcode": "900011", "respmsg": "主体数据为空，请注意是否具有操作权限!"})
# return HttpResponse(s)


#用户登录
def login(request, reqest_body):
    log = public.logger
    log.info('----------------------Admin-login-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "登录成功！",
        "trantype": reqest_body.get('trantype', None)
    }

    username=reqest_body.get('username',None)
    password=reqest_body.get('password',None)
    if username and password:
        try:
            # 根据前台传回的用户名查找密码和用户状态
            # 若查询失败，抛出异常错误
            # 若查询成功，判断密码是否正确和用户状态是否正常
            tmp_password = User.objects.get(username=username).password
            tmp_status = User.objects.get(username=username).status
            uid = User.objects.get(username = username).user_id
        except:
            s = public.setrespinfo({"respcode": "100001", "respmsg": "用户不存在,请先注册！"})
            return HttpResponse(s)
        else:
            if password == tmp_password and 0 == tmp_status:
                request.session["username"] = username
            else:
                s = public.setrespinfo({"respcode": "100002", "respmsg": "密码错误！"})
                return HttpResponse(s)
    else:
        s = public.setrespinfo({"respcode": "100003", "respmsg": "缺少必要参数！"})
        return HttpResponse(s)
    jsondata['uid'] = uid

    s = json.dumps(jsondata, cls=JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-login-end---------------------------')
    return HttpResponse(s)


#用户注册
def register(request, reqest_body):
    log = public.logger
    log.info('----------------------Admin-register-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "注册成功！",
        "trantype": reqest_body.get('trantype', None),
    }

    username=reqest_body.get('username',None)
    password=reqest_body.get('password',None)
    nowTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if username and password:  # 用户名和密码不为空时，执行操作
        # 将用户名和密码，以及初始状态status=0插入数据库中
        # 若插入失败，抛出异常操作失败
        # 若插入成功，返回成功信息
        try:
            sql = "select * from zbookapp_user where username=%s"
            cur = connection.cursor()
            log.info(sql%username)
            cur.execute(sql,username)
            row = cur.fetchall()
            if row:
                s = public.setrespinfo({"respcode": "100004", "respmsg": "用户名已被注册！"})
                return s
            else:
                User.objects.create(username=username, password=password,tran_date=nowTime)
        except Exception as e:
            s = public.setrespinfo({"respcode": "100005", "respmsg": "注册失败！"})
            return s
    else:
        s = public.setrespinfo({"respcode": "100006", "respmsg": "缺少必要参数！"})
        return s

    s = json.dumps(jsondata, cls=JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-register-end---------------------------')
    return HttpResponse(s)

#退出登录
def exit(request, reqest_body):
    log = public.logger
    log.info('----------------------Admin-exit-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "已退出！",
        "trantype": reqest_body.get('trantype', None),
    }

    try:
        del request.session['username']
    except:
        s = public.setrespinfo({"respcode": "100004", "respmsg": "操作失败！"})
        return s

    s = json.dumps(jsondata, cls=JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-exit-end---------------------------')
    return HttpResponse(s)

#检查登录session
def logincheck(request, reqest_body):
    log = public.logger
    log.info('----------------------Admin-logincheck-begin---------------------------')
    jsondata = {
        "respcode": "000000",
        "respmsg": "已退出！",
        "trantype": reqest_body.get('trantype', None),
    }

    try:
        username = request.session.get('username')
    except:
        s = public.setrespinfo({"respcode": "100004", "respmsg": "操作失败！"})
        return s
    else:
        if username:
            jsondata['username'] = username
        else:
            s = public.setrespinfo({"respcode": "100005", "respmsg": "未登录！"})
            return s

    s = json.dumps(jsondata, cls=JsonCustomEncoder, ensure_ascii=False)
    log.info('----------------------Admin-logincheck-end---------------------------')
    return HttpResponse(s)










