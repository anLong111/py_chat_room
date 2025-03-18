# coding: utf-8
# @Author: 小飞有点东西
"""
核心逻辑
"""
from multiprocessing import Process, Manager

from lib.common import *
from core.urls import route_mode


class ChatServer:
    def __init__(self, host='localhost', port=9000, q_list=None, idx=0, users_list=None):
        self.host = host
        self.port = port
        MyConn.q_list = q_list
        MyConn.bcst_q = q_list[idx]
        MyConn.users_list = users_list

        asyncio.run(asyncio.wait([self.run_server(), MyConn.send_all()]))

    async def client_handler(self, reader, writer):
        print('进程号:', os.getpid(), '端口号:', self.port)
        async with MyConn(reader, writer) as conn:
            while True:
                request_dic = await conn.recv()
                fn = route_mode.get(request_dic.get('mode'))
                await fn(conn, request_dic)

    async def run_server(self):
        server = await asyncio.start_server(self.client_handler, self.host, self.port)
        async with server:
            LOGGER.debug('服务端启动成功 {}'.format((self.host, self.port)))
            await server.serve_forever()


def run():
    users_list = Manager().list()

    cpu_count = 2
    q_list = [Queue() for _ in range(cpu_count)]

    # 工具：监听9000 -> 服务端(9001, 9002......)
    for i in range(1, cpu_count):
        Process(target=ChatServer, args=(HOST, PORT + i, q_list, i, users_list)).start()

    ChatServer(HOST, PORT + cpu_count, q_list, 0, users_list)
