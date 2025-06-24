# coding: utf-8
# @Author: 小安
"""
配置文件
"""
import os
import logging.config

# 服务器地址配置
HOST = '0.0.0.0'
PORT = 9000


# 协议配置
RESPONSE_SUCCESS_CODE = 200
RESPONSE_ERROR_CODE = 400
RESPONSE_REGISTER = 'register'
RESPONSE_LOGIN = 'login'
RESPONSE_BROADCAST = 'broadcast'
RESPONSE_ONLINE = 'online'
RESPONSE_OFFLINE = 'offline'
RESPONSE_CHAT = 'chat'
RESPONSE_FILE = 'file'
RESPONSE_RECONNECT = 'reconnect'
PROTOCOL_LENGTH = 8

# 群公告
NOTCIE = '请文明发言！'


# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(__file__))       # 项目根目录
INFO_LOG_DIR = os.path.join(BASE_DIR, 'log', 'info.log')
ERROR_LOG_DIR = os.path.join(BASE_DIR, 'log', 'error.log')
ASYNCIO_ERROR_LOG_DIR = os.path.join(BASE_DIR, 'log', 'asyncio_error.log')
USER_DIR = os.path.join(BASE_DIR, 'db', 'users')


FILE_DIR = os.path.join(BASE_DIR, 'db', 'files')


LEVEL = 'INFO'

# 日志配置字典
LOGGING_DIC = {
    'version': 1.0,
    'disable_existing_loggers': False,
    # 日志格式
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(threadName)s:%(thread)d [%(name)s] %(levelname)s [%(pathname)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(asctime)s [%(name)s] %(levelname)s  %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'test': {
            'format': '%(asctime)s %(message)s',
        },
    },
    'filters': {},
    # 日志处理器
    'handlers': {
        'console_debug_handler': {
            'level': LEVEL,  # 日志处理的级别限制
            'class': 'logging.StreamHandler',  # 输出到终端
            'formatter': 'simple'  # 日志格式
        },
        'file_info_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'filename': INFO_LOG_DIR,
            'maxBytes': 1024*1024*10,  # 日志大小 10M
            'backupCount': 10,  # 日志文件保存数量限制
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'file_error_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'filename': ERROR_LOG_DIR,
            'maxBytes': 1024*1024*10,  # 日志大小 10M
            'backupCount': 10,  # 日志文件保存数量限制
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'file_asyncio_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'filename': ASYNCIO_ERROR_LOG_DIR,
            'maxBytes': 1024*1024*10,  # 日志大小 10M
            'backupCount': 10,  # 日志文件保存数量限制
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
    },
    # 日志记录器
    'loggers': {
        '': {  # 导入时logging.getLogger时使用的app_name
            'handlers': ['console_debug_handler', 'file_info_handler'],  # 日志分配到哪个handlers中
            'level': 'DEBUG',  # 日志记录的级别限制
            'propagate': False,  # 默认为True，向上（更高级别的logger）传递，设置为False即可，否则会一份日志向上层层传递
        },
        'error_logger': {  # 导入时logging.getLogger时使用的app_name
            'handlers': ['file_error_handler'],  # 日志分配到哪个handlers中
            'level': 'ERROR',  # 日志记录的级别限制
            'propagate': False,  # 默认为True，向上（更高级别的logger）传递，设置为False即可，否则会一份日志向上层层传递
        },
        'asyncio': {  # 导入时logging.getLogger时使用的app_name
            'handlers': ['file_asyncio_handler'],  # 日志分配到哪个handlers中
            'level': 'ERROR',  # 日志记录的级别限制
            'propagate': False,  # 默认为True，向上（更高级别的logger）传递，设置为False即可，否则会一份日志向上层层传递
        },
    }
}

logging.config.dictConfig(LOGGING_DIC)
LOGGER = logging.getLogger('server')
ERROR_LOGGER = logging.getLogger('error_logger')
