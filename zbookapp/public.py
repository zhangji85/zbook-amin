__author__ = 'litz'

import os
import datetime
import string
import logging
import logging.handlers
import pymysql
import json
from zbookapp import models
import random
from django.shortcuts import  HttpResponse
import calendar

localhome='E:\\zbookAdmin\\'#本地目录
localurl='http://127.0.0.1:8000'#本地目录

DevIpList={
    "192.168.2.15":"http://192.168.2.15:8080/",
}

#日志初始化,日志名称
global logger, fh
logger = logging.getLogger(str(os.getpid()))
def loger_init( logname ):
    #日志初始化
    now_time = datetime.datetime.now().strftime('%Y%m%d')
    logger = logging.getLogger(str(os.getpid()))
    logger.setLevel(logging.INFO)
    if os.path.exists(localhome+'logs/'):
        log_file_temp = localhome+'logs/'+logname+'_'+now_time+'.log'
    else:
        log_file_temp = logname + '_' + now_time + '.log'
    # fh = logging.FileHandler(log_file_temp)  # 定义一个写文件的handler
    fh = logging.handlers.RotatingFileHandler(log_file_temp, maxBytes=1024*1024*100, backupCount=30)
    fh.setLevel(logging.INFO)  # 设置写文件的等级
    fh_formatter = logging.Formatter(
        '[%(levelname)-5s] [%(filename)-12s line:%(lineno)-4d] [%(asctime)s] [%(process)-7d] [%(message)s]')  # 设置输出格式
    fh.setFormatter(fh_formatter)  # 将输出格式设置给handler
    if  not logger.handlers:
        logger.addHandler(fh)  # 将handler加入logger
    return logger, fh

#返回信息转换为json格式
def setrespinfo(resp):
    s = json.dumps(resp, cls=models.JsonCustomEncoder, ensure_ascii=False)
    return HttpResponse(s)