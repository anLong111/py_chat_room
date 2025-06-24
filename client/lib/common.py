# coding: utf-8
# @Author: 小安
"""
公共方法
"""
import hashlib
from datetime import datetime, timezone
from PyQt6.QtWidgets import QMessageBox
from conf.settings import *


# 哈希加密
def hash_pwd(pwd):
    hash_obj = hashlib.sha256()
    hash_obj.update('vx'.encode('utf-8'))
    hash_obj.update(pwd.encode('utf-8'))
    hash_obj.update('d1303544500'.encode('utf-8'))
    return hash_obj.hexdigest()


def get_time():
    return datetime.now().replace(microsecond=0)


def get_file_info(file_path):
    file_name = os.path.basename(file_path)
    hash_obj = hashlib.md5()
    with open(file_path, 'rb')as f:
        f.seek(0, 2)
        file_size = f.tell()
        one_tenth = file_size // 10
        for i in range(10):
            f.seek(i * one_tenth, 0)
            res = f.read(100)
            hash_obj.update(res)
        return file_name, file_size, hash_obj.hexdigest()


# 重连处理装饰器
def reconnect(fn):
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            res = fn(*args, **kwargs)
        except Exception as e:
            print(e)
            LOGGER.error('连接断开，正在重连 {}'.format(e))
            self.tip_label.setText('连接断开，正在重连...')
            self.tip_label.setFixedSize(self.tip_label.size())
            self.tip_label.adjustSize()
            self.tip_label.show()
            self.client.close()
            res = self.client.connect()
            self.tip_label.close()
            if res:
                return
            QMessageBox.warning(self, '提示', '连接服务器失败，即将关闭程序')
            exit()
        return res
    return wrapper


# 重连处理装饰器
def reconnect_t(fn):
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            res = fn(*args, **kwargs)
        except Exception as e:
            LOGGER.error('连接断开，正在重连 {}'.format(e))
            # 信号
            self.reconnected.emit('show_tip')

            self.client.close()
            res = self.client.connect()

            # 信号
            self.reconnected.emit('close_tip')
            if res:
                return
            # 信号
            self.reconnected.emit('over')
            self.terminate()

        return res
    return wrapper


def byte_to_human(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        if size < 1024 or unit == 'PB':
            return '{:.2f} {}'.format(size, unit)
        size /= 1024

class RequestData:
    @staticmethod
    def register_dic(user, pwd, *args, **kwargs):
        """
        组织注册字典
        :param user:
        :param pwd:
        :param args:
        :param kwargs:
        :return:
        """
        request_dic = {
            'mode': REQUEST_REGISTER,
            'user': user,
            'pwd': hash_pwd(pwd)
        }
        return request_dic

    @staticmethod
    def login_dic(user, pwd, *args, **kwargs):
        """
        组织登陆字典
        :param user:
        :param pwd:
        :param args:
        :param kwargs:
        :return:
        """
        request_dic = {
            'mode': REQUEST_LOGIN,
            'user': user,
            'pwd': hash_pwd(pwd)
        }
        return request_dic

    @staticmethod
    def chat_dic(user, msg, token, *args, **kwargs):
        """
        组织聊天字典
        :param user:
        :param msg:
        :param token:
        :param args:
        :param kwargs:
        :return:
        """
        request_dic = {
            'mode': REQUEST_CHAT,
            'user': user,
            'msg': msg,
            'time': get_time(),
            'token': token
        }
        return request_dic

    @staticmethod
    def file_dic(user, file_path, token, *args, **kwargs):
        """
        组织文件字典
        :param user:
        :param file_path:
        :param token:
        :param args:
        :param kwargs:
        :return:
        """
        file_name, file_size, file_md5 = get_file_info(file_path)
        request_dic = {
            'mode': REQUEST_FILE,
            'user': user,
            'file_name': file_name,
            'file_size': file_size,
            'md5': file_md5,
            'time': get_time(),
            'token': token,
            'file_path': file_path
        }
        return request_dic

    @staticmethod
    def reconnect_dic(user, token, *args, **kwargs):
        """
        组织重连字典
        :param user:
        :param token:
        :param args:
        :param kwargs:
        :return:
        """
        request_dic = {
            'mode': REQUEST_RECONNECT,
            'user': user,
            'token': token
        }
        return request_dic
