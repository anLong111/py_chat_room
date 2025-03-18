# coding: utf-8
# Auther: 小安
import asyncio
import socket

async def client_connected(reader, writer):
    while True:
        data = await reader.read(1024)
        if not data:
            break
        writer.write('hello'.encode('utf-8'))
        print(data)


async def main():
    server = await asyncio.start_server(client_connected, 'localhost', 9000)
    async with server:
        await server.serve_forever()


asyncio.run(main())








