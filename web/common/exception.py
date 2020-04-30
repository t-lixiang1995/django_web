# @Time : 2020/4/28 14:02 
# @Author : lixiang
# @File : exception.py 
# @Software: PyCharm
from rest_framework.views import exception_handler
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework import status

import logging

from web.common.MyLogger import Logger
from web.common.errors import BaseError, OrmError

logger = logging.getLogger("web")  # 与settings中一致


def custom_exception_handler(exc, context):
    """
    自定义的异常处理
    :param exc:     本次请求发送的异常信息
    :param context: 本次请求发送异常的执行上下文【本次请求的request对象，异常发送的时间，行号等....】
    :return:
    """
    response = exception_handler(exc, context)
    if response is None:
        """来到这只有2中情况，要么程序没出错，要么就是出错了而Django或者restframework不识别"""
        view = context['view']
        if isinstance(exc, DatabaseError):
            # 数据库异常
            """有5个方法发debug info error critical warning"""
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': '服务器内部错误，请联系客服工作人员！'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        if isinstance(exc, BaseError):
            if exc.level in [BaseError.LEVEL_INFO, BaseError.LEVEL_WARN, BaseError.LEVEL_ERROR]:
                if isinstance(exc, OrmError):
                    logger.error('%s %s' % (exc.parent_error, exc))
                else:
                    if exc.level is BaseError.LEVEL_INFO:
                        Logger().logger.info('INFO信息: %s %s' % (exc.extras, exc))
                        # app.logger.info('INFO信息: %s %s' % (e.extras, e))
                    elif exc.level is BaseError.LEVEL_WARN:
                        Logger('error.log', level='error').logger.error('告警信息: %s %s' % (exc.extras, exc))
                        # app.logger.error('告警信息: %s %s' % (e.extras, e))
                    else:
                        Logger('error.log', level='error').logger.error('错误信息: %s %s' % (exc.extras, exc))
                        # app.logger.error('错误信息: %s %s' % (e.extras, e))
            response = Response(exc.to_dict())
            response.status_code = exc.status_code
    return response