# coding: utf-8
# @Author: 小飞有点东西
# 资料下载：https://active.clewm.net/FrcyFA
import socket

client = socket.socket()


client.connect(('localhost', 9000))     # 可能会连接失败，加入异常判断
while True:
    client.send('hello'.encode("utf-8"))
    recv_data = client.recv(1024)
    if not recv_data:
        break
    print(recv_data.decode('utf-8'))
