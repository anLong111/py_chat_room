# coding: utf-8
# @Author: 小安

from db.models import User
from lib.common import *


async def register(conn, request_dic, *args, **kwargs):
    """
    注册接口
    :param conn:
    :param request_dic:
    :param args:
    :param kwargs:
    :return:
    """
    LOGGER.debug('开始注册')
    user = request_dic.get('user')
    pwd = request_dic.get('pwd')
    if await User.select(user):
        response_dic = ResponseData.register_error_dic('用户 【{}】 已存在，请更换用户名'.format(user))
        await conn.send(response_dic)
        return
    user_obj = User(user, pwd)
    await user_obj.save()
    response_dic = ResponseData.register_success_dic('注册成功')
    await conn.send(response_dic)


async def login(conn, request_dic, *args, **kwargs):
    """
    登陆接口
    :param conn:
    :param request_dic:
    :param args:
    :param kwargs:
    :return:
    """
    LOGGER.debug('开始登陆')
    user = request_dic.get('user')
    pwd = request_dic.get('pwd')
    user_obj = await User.select(user)
    if not user_obj or user_obj.pwd != pwd:
        response_dic = ResponseData.login_error_dic(user, '用户名或密码错误')
        await conn.send(response_dic)
        return

    if user in conn.users_list:
        response_dic = ResponseData.login_error_dic(user, '请不要重复登陆')
        await conn.send(response_dic)
        return

    # 保存当前的conn对象
    conn.users_list.append(user)
    conn.online_users[user] = conn
    conn.name = user
    conn.token = generate_token(user)
    LOGGER.info('【{}】进入了聊天室'.format(user))
    response_dic = ResponseData.login_success_dic(user, conn.token, '登陆成功')
    await conn.send(response_dic)

    # 广播消息
    response_dic = ResponseData.online_dic(user)
    await conn.put_q(response_dic)


async def reconnect(conn, request_dic, *args, **kwargs):
    """
    重连接口
    :param conn:
    :param request_dic:
    :param args:
    :param kwargs:
    :return:
    """
    LOGGER.debug('开始重连')
    token = request_dic.get('token')
    user = request_dic.get('user')
    if generate_token(user) != token:
        response_dic = ResponseData.reconnect_error_dic('token无效，请重新登陆')
        await conn.send(response_dic)
        return

    if user in conn.users_list:
        response_dic = ResponseData.reconnect_error_dic('已经在其他地方登陆')
        await conn.send(response_dic)
        return

    # 保存当前的conn对象
    conn.users_list.append(user)
    conn.online_users[user] = conn
    conn.name = user
    conn.token = token
    LOGGER.info('【{}】进入了聊天室'.format(user))
    response_dic = ResponseData.reconnect_success_dic()
    await conn.send(response_dic)

    # 广播消息
    response_dic = ResponseData.online_dic(user)
    await conn.put_q(response_dic)


async def chat(conn, request_dic, *args, **kwargs):
    """
    聊天接口
    :param conn:
    :param request_dic:
    :param args:
    :param kwargs:
    :return:
    """
    token = request_dic.get('token')
    if token != conn.token:
        conn.close()
        return
    user = request_dic.get('user')
    msg = request_dic.get('msg')
    LOGGER.info('{}说：{}'.format(user, msg))
    response_dic = ResponseData.chat_dic(request_dic)
    await conn.put_q(response_dic)


async def file(conn, request_dic, *args, **kwargs):
    """
    文件接口
    :param conn:
    :param request_dic:
    :param args:
    :param kwargs:
    :return:
    """
    token = request_dic.get('token')
    if token != conn.token:
        conn.close()
        return

    user = request_dic.get('user')
    file_name = request_dic.get('file_name')
    LOGGER.info('{}发了文件：{}'.format(user, file_name))
    response_dic = ResponseData.file_dic(request_dic)
    await conn.put_q(response_dic)


