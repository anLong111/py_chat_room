# coding: utf-8
# @Author: 小飞有点东西
"""
入口文件
"""

from core import client
from PyQt6 import QtWidgets


QtWidgets.QTextEdit = client.MyTextEdit


if __name__ == '__main__':
    client.run()
