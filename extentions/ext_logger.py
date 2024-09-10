import os
import logging
from logging.handlers import TimedRotatingFileHandler
import uuid
import pytz
from datetime import datetime
from fastapi import FastAPI
from configs import config
from middlewares import request_id_ctx_var
    
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        request_id = request_id_ctx_var.get(None)
        record.request_id = request_id if request_id else 'N/A'
        return True
    
def setup_logger(app: FastAPI):
    # 确保日志目录存在
    if not os.path.exists('storage/logs/fastapi'):
        os.makedirs('storage/logs/fastapi')



    # 创建过滤器并添加到处理器中
    request_id_filter = RequestIdFilter()

    # 创建按小时分割的日志处理器
    timed_handler = TimedRotatingFileHandler(
        'storage/logs/fastapi/app.log', 
        when=config.LOG_WHEN,   
        interval=config.LOG_INTERVAL,   
        backupCount=config.LOG_BACKUPCOUNT  
    )
    timed_handler.addFilter(request_id_filter)
    timed_handler.setLevel(config.LOG_LEVEL)
    timed_handler.setFormatter(logging.Formatter(
        fmt=config.LOG_FORMAT
    ))

    # 添加控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.addFilter(request_id_filter)
    console_handler.setLevel(config.LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(
        fmt=config.LOG_FORMAT,
        datefmt=config.LOG_DATEFORMAT
    ))

    # init log
    log_handlers = [
        timed_handler, console_handler,
    ]
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATEFORMAT,
        handlers=log_handlers
    )
    
    log_tz = config.LOG_TZ
    if log_tz:
        timezone = pytz.timezone(log_tz)

        def time_converter(seconds):
            dt_utc = datetime.fromtimestamp(seconds, tz=timezone)
            dt_local = dt_utc.astimezone(timezone)
            return dt_local.timetuple()

        for handler in logging.root.handlers:
            handler.formatter.converter = time_converter