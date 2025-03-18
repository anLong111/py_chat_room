# coding: utf-8
# @Author: 小飞有点东西
"""
公共方法
"""
import re
import asyncio
import pickle
import hashlib
import aiofiles
from datetime import datetime, timezone
from multiprocessing import Queue
from conf.settings import *


# 生成token
def generate_token(user):
    hash_obj = hashlib.sha256()
    hash_obj.update(user.encode('utf-8'))
    hash_obj.update(str(datetime.now().date()).encode('utf-8'))  # token 会根据用户登录的日期和用户名生成唯一的token值
    hash_obj.update('小飞有点东西'.encode('utf-8'))
    return hash_obj.hexdigest()


def get_utc_time():
    utc_time = datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc)
    return utc_time

class ResponseData:
    notice = NOTCIE

    @staticmethod
    def register_success_dic(msg, *args, **kwargs):
        """
        组织注册成功字典
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic = {
            'code': RESPONSE_SUCCESS_CODE,
            'mode': RESPONSE_REGISTER,
            'msg': msg
        }
        return response_dic

    @staticmethod
    def register_error_dic(msg, *args, **kwargs):
        """
        注册失败字典
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic = {
            'code': RESPONSE_ERROR_CODE,
            'mode': RESPONSE_REGISTER,
            'msg': msg
        }
        return response_dic

    @staticmethod
    def login_success_dic(user, token, msg, *args, **kwargs):
        """
        登陆成功字典
        :param token:
        :param user:
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic = {
            'code': RESPONSE_SUCCESS_CODE,
            'mode': RESPONSE_LOGIN,
            'user': user,
            'msg': msg,
            'token': token,
            'notice': ResponseData.notice,
            'users': tuple(MyConn.users_list),
        }
        return response_dic

    @staticmethod
    def login_error_dic(user, msg, *args, **kwargs):
        """
        登陆失败字典
        :param user:
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic = {
            'code': RESPONSE_ERROR_CODE,
            'mode': RESPONSE_LOGIN,
            'user': user,
            'msg': msg
        }
        return response_dic

    @staticmethod
    def online_dic(user, *args, **kwargs):
        """
        上线广播字典
        :param user:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic = {
            'code': RESPONSE_SUCCESS_CODE,
            'mode': RESPONSE_BROADCAST,
            'status': RESPONSE_ONLINE,
            'user': user,
        }
        return response_dic

    @staticmethod
    def offline_dic(user, *args, **kwargs):
        """
        下线广播字典
        :param user:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic = {
            'code': RESPONSE_SUCCESS_CODE,
            'mode': RESPONSE_BROADCAST,
            'status': RESPONSE_OFFLINE,
            'user': user,
        }
        return response_dic

    @staticmethod
    def reconnect_success_dic(*args, **kwargs):
        """
        重连成功字典
        :param args:
        :param kwargs:
        :return:
        """
        response_dic = {
            'code': RESPONSE_SUCCESS_CODE,
            'mode': RESPONSE_RECONNECT,
            'users': tuple(MyConn.users_list)
        }
        return response_dic

    @staticmethod
    def reconnect_error_dic(msg, *args, **kwargs):
        """
        重连失败字典
        :param msg:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic = {
            'code': RESPONSE_ERROR_CODE,
            'mode': RESPONSE_RECONNECT,
            'msg': msg
        }
        return response_dic

    @staticmethod
    def chat_dic(response_dic, *args, **kwargs):
        """
        聊天字典
        :param response_dic:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic.pop('token')
        response_dic['code'] = RESPONSE_SUCCESS_CODE
        response_dic['time'] = get_utc_time()
        return response_dic

    @staticmethod
    def file_dic(response_dic, *args, **kwargs):
        """
        文件字典
        :param response_dic:
        :param args:
        :param kwargs:
        :return:
        """
        response_dic.pop('token')
        response_dic['code'] = RESPONSE_SUCCESS_CODE
        response_dic['time'] = get_utc_time()
        return response_dic


class MyConn:
    # 类属性
    online_users = {}
    bcst_q = None
    q_list = None
    users_list = None
    offline_users = []

    def __init__(self, reader, writer):
        # 对象属性
        self.reader = reader
        self.writer = writer

        self.name = None
        self.token = None

    async def put_q(self, dic):
        loop = asyncio.get_running_loop()
        for q in self.q_list:
            await loop.run_in_executor(None, q.put, dic)

    @classmethod
    async def send_all(cls):
        loop = asyncio.get_running_loop()

        while True:
            # 开线程，将进程队列中的字典获取
            dic = await loop.run_in_executor(None, cls.bcst_q.get)

            # 获取file_path
            try:
                file_path = dic.pop('file_path')
            except KeyError:
                pass

            # 将字典发送给每一个上线用户列表，除了自己
            for conn in cls.online_users.values():
                if conn.name == dic.get('user'):
                    continue
                print(f'发送给{conn.name}, 发送内容{dic}')
                await conn.send(dic)


            # 如果是文件， 发送文件
            if dic.get('mode') == RESPONSE_FILE:
                await cls.send_file(dic, file_path)

            # 遍历下线用户字典，并删除
            for user in cls.offline_users:
                cls.online_users.pop(user)

            cls.offline_users.clear()

    @classmethod
    async def send_file(cls, dic, file_path):
        async with aiofiles.open(file_path, 'rb')as f:
            while True:
                # 收取数据
                temp = await f.read(4096)
                if not temp:
                    break
                # 发送给每一个在线用户列表
                for conn in cls.online_users.values():
                    if conn.name == dic.get('user'):
                        continue
                    await conn.write(temp)

    async def write(self, data):
        self.writer.write(data)
        await self.writer.drain()

    async def send(self, dic):
        dic_bytes = pickle.dumps(dic)
        len_bytes = len(dic_bytes).to_bytes(PROTOCOL_LENGTH, byteorder='big')
        await self.write(len_bytes)
        await self.write(dic_bytes)
        LOGGER.debug('发送字典完成')
        if dic.get('mode') != RESPONSE_FILE:
            return

    async def read(self, recv_len):
        return await self.reader.read(recv_len)

    async def recv(self):
        len_bytes = await self.read(PROTOCOL_LENGTH)
        if not len_bytes:
            raise ConnectionResetError
        stream_len = int.from_bytes(len_bytes, byteorder='big')
        dic_bytes = bytes()
        while stream_len > 0:
            if stream_len < 4096:
                temp = await self.read(stream_len)
            else:
                temp = await self.read(4096)
            if not temp:
                raise ConnectionResetError
            dic_bytes += temp
            stream_len -= len(temp)
        request_dic = pickle.loads(dic_bytes)
        if request_dic.get('mode') != RESPONSE_FILE:
            return request_dic
        # 接收文件数据
        return await self.recv_file(request_dic)

    @staticmethod
    def rename(file_name):
        base, ext = os.path.splitext(file_name)
        pattern = re.compile(r'\((\d+)\)$')
        res = pattern.search(base)
        if res:
            num = int(res.group(1)) + 1
            base = pattern.sub('({})'.format(num), base)
        else:
            base = '{}{}'.format(base, '(1)')
        return '{}{}'.format(base, ext)

    async def recv_file(self, request_dic):
        file_size = request_dic.get('file_size')
        now_date = datetime.now().strftime('%Y-%m')
        file_dir = os.path.join(FILE_DIR, now_date)
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)

        file_name = request_dic.get('file_name')
        file_path = os.path.join(file_dir, file_name)
        while True:
            if os.path.exists(file_path):
                file_name = self.rename(file_name)
                file_path = os.path.join(file_dir, file_name)
            else:
                break
        async with aiofiles.open(file_path, 'wb')as f:
            while file_size > 0:
                if file_size < 4096:
                    temp = await self.read(file_size)
                else:
                    temp = await self.read(4096)
                if not temp:
                    raise ConnectionResetError
                await f.write(temp)
                file_size -= len(temp)
            request_dic['file_path'] = file_path
        return request_dic


    def close(self):

        self.writer.close()

    async def offline(self):
        self.users_list.pop(self.users_list.index(self.name))
        self.offline_users.append(self.name)
        LOGGER.info('【{}】离开了聊天室'.format(self.name))
        response_dic = ResponseData.offline_dic(self.name)
        await self.put_q(response_dic)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if self.name:
            await self.offline()

        if exc_type is ConnectionResetError:
            return True

        if (exc_type is not None) and LEVEL != 'DEBUG':
            ERROR_LOGGER.error('{}: {} {}'.format(
                exc_type.__name__, exc_val, exc_tb.tb_frame
            ))
            return True






