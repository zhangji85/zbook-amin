from django.shortcuts import render,HttpResponse
import datetime
from zbookapp import public
from django.db import connection, transaction
from zbookapp.useraction import useract
from zbookapp.filedue import filecfg
from zbookapp.readaction import readact
from zbookapp.appact import appreadact
from zbookapp.appact import appuseract
from zbookapp.appact import appview
from django.views.decorators.csrf import csrf_exempt,csrf_protect

# Create your views here.
# @csrf_exempt  不用CSRF防护
@csrf_exempt
def admin(request):
    try:
        starttime = datetime.datetime.now()
        global log
        log, fh = public.loger_init('Admin')
        log.info('----------------------Admin-begin---------------------------')
        log.info("请求:[%s]" % request)
        log.info("请求path:[%s]" % request.path)
        log.info("请求method:[%s]" % request.method)
        log.info("请求GET:[%s]" % request.GET)

        global location_href
        location_href = 'https://localhost:8000' + request.get_full_path()
        log.info("请求full_path:[%s]" % location_href)
        if request.path[-1] == '/':
            param1 = request.path.rsplit('/')[-2]
        else:
            param1 = request.path.rsplit('/')[-1]
        logmsg = 'param1=[' + param1 + ']'
        log.info(logmsg)

        global respinfo
        respinfo = None

        # 记录交易处理开始的时间点
        mysavepoint = transaction.savepoint()

        if param1 == 'useract':
            # 登录、注册接口
            respinfo = useract.admin(request)
            return respinfo
        elif param1 == 'filecfg':
            # 文件上传接口
            respinfo = filecfg.admin(request)
            return respinfo
        elif param1 == 'readact':
            # 阅读接口
            respinfo = readact.admin(request)
            return respinfo
        elif param1 == 'appview':
            # app信息展示
            respinfo = appview.admin(request)
            return respinfo
        elif param1 == 'appreadact':
            # app阅读接口
            respinfo = appreadact.admin(request)
            return respinfo
        elif param1 == 'appuseract':
            # app用户个人信息操作接口
            respinfo = appuseract.admin(request)
            return respinfo
        else:
            respinfo = render(request, 'index.html')
            return respinfo
    except Exception as e :
        log.error('程序运行错误', exc_info = True)
        try:
            transaction.savepoint_rollback(mysavepoint)
        except:
            pass

        s = public.setrespinfo({"respcode": "999999", "respmsg": "系统错误:"+str(e)})
        respinfo=HttpResponse(s)

    finally:
        try:
            transaction.savepoint_rollback(mysavepoint)
        except:
            pass
        if not respinfo:  # 如果返回信息为空
            s = public.setrespinfo({"respcode": "999999", "respmsg": "系统错误[返回数据异常]"})
            respinfo = HttpResponse(s)

        try:
            if len(str(respinfo)) < 1024:
                log.info(respinfo)
                log.info(respinfo.getvalue().decode(encoding='utf-8'))
        except:
            pass
        log.info('----------------------Admin-end---------------------------')
        log.info('交易处理时间: %s' % str(datetime.datetime.now() - starttime))
        if fh:
            fh.close()
            log.removeHandler(fh)
        return respinfo

