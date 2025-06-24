# coding: utf-8
# @Author: 小安
"""
核心逻辑
"""
import os
import re
import socket
import time
import pickle
import queue
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QLabel, QListWidgetItem, QFileIconProvider
from PyQt6.QtCore import Qt, QCoreApplication, QThread, pyqtSignal, QTimer, QMargins, QFileInfo
from PyQt6.QtGui import QDropEvent, QImage

from lib.common import *
from ui.login import Ui_Form as LoginUiMixin
from ui.chat import Ui_Form as ChatUiMixin


class MyTextEdit(QTextEdit):
    returnPressed = pyqtSignal()
    drop_event = pyqtSignal(list)

    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key.Key_Return and not e.modifiers():
            self.returnPressed.emit()
            return
        super().keyPressEvent(e)

    def dropEvent(self, e: QDropEvent) -> None:
        urls = []
        q_urls = e.mimeData().urls()
        for q_url in q_urls:
            url = q_url.toLocalFile()
            if os.path.isfile(url):
                urls.append(url)
        if not urls:
            return
        self.drop_event.emit(urls)


class MySocket:
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        self.user = None
        self.token = None
        self.socket = None

    def send(self, data):
        self.socket.send(data)

    def recv(self, recv_len):
        return self.socket.recv(recv_len)

    def recv_data(self):
        len_bytes = self.recv(PROTOCOL_LENGTH)
        if not len_bytes:
            raise ConnectionResetError
        stream_len = int.from_bytes(len_bytes, byteorder='big')
        dic_bytes = bytes()
        while stream_len > 0:
            if stream_len < 4096:
                temp = self.recv(stream_len)
            else:
                temp = self.recv(4096)
            if not temp:
                raise ConnectionResetError
            dic_bytes += temp
            stream_len -= len(temp)
        response_dic = pickle.loads(dic_bytes)
        if response_dic.get('mode') != REQUEST_FILE:
            return response_dic
        # 接收文件数据
        return self.recv_file(response_dic)

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

    def recv_file(self, response_dic):
        file_size = response_dic.get('file_size')
        now_date = datetime.now().strftime('%Y-%m')
        file_dir = os.path.join(FILE_DIR, now_date)
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)

        file_name = response_dic.get('file_name')
        file_path = os.path.join(file_dir, file_name)
        while True:
            if os.path.exists(file_path):
                file_name = self.rename(file_name)
                file_path = os.path.join(file_dir, file_name)
            else:
                response_dic['file_name'] = file_name
                break
        with open(file_path, 'wb') as f:
            while file_size > 0:
                if file_size < 4096:
                    temp = self.recv(file_size)
                else:
                    temp = self.recv(4096)
                if not temp:
                    raise ConnectionResetError
                f.write(temp)
                file_size -= len(temp)
            response_dic['file_path'] = file_path
        return response_dic

    def send_data(self, dic):
        try:
            file_path = dic.pop('file_path')
        except KeyError:
            pass
        dic_bytes = pickle.dumps(dic)
        len_bytes = len(dic_bytes).to_bytes(PROTOCOL_LENGTH, byteorder='big')
        self.send(len_bytes)
        self.send(dic_bytes)
        LOGGER.debug('发送字典完成')
        if dic.get('mode') != REQUEST_FILE:
            return

        # 发送文件
        with open(file_path, 'rb')as f:
            while True:
                temp = f.read(4096)
                if not temp:
                    break
                self.send(temp)

    def connect(self):
        for i in range(1, 4):
            try:
                self.socket = socket.socket()
                self.socket.connect((self.host, self.port))
                LOGGER.debug('连接服务器成功！')
                return True
            except Exception as e:
                ERROR_LOGGER.error('连接服务器失败，开始第{}次重连 {}'.format(i, e))
                self.socket.close()
            time.sleep(2)

    def close(self):
        self.socket.close()

    def __enter__(self):
        if self.connect():
            return self
        else:
            exit()
            # return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class LoginWindow(LoginUiMixin, QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setupUi(self)
        self.tip_label = QLabel()
        self.tip_label.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # 隐藏边框
        self.tip_label.setWindowModality(Qt.WindowModality.ApplicationModal)  # 模态窗口
        self.tip_label.setStyleSheet("background-color: gray")

        self.chat_window = None
        self.test()

    @reconnect
    def get(self, dic):
        self.client.send_data(dic)  # 发送数据
        response_dic = self.client.recv_data()  # 接收数据
        return response_dic

    def register(self):
        LOGGER.debug('注册')
        user = self.lineEdit_3.text().strip()
        pwd = self.lineEdit_4.text().strip()
        re_pwd = self.lineEdit_5.text().strip()
        if not user or not pwd or not re_pwd:
            QMessageBox.warning(self, '警告', '请填写完整！')
            return
        if pwd != re_pwd:
            QMessageBox.warning(self, '警告', '两次密码不一致！')
            return
        request_dic = RequestData.register_dic(user, pwd)
        response_dic = self.get(request_dic)
        if not response_dic:  # 重连成功
            return
        QMessageBox.about(self, '提示', response_dic.get('msg'))
        if response_dic.get('code') != 200:
            return

        self.lineEdit_3.setText('')
        self.lineEdit_4.setText('')
        self.lineEdit_5.setText('')
        self.open_login_page()
        self.lineEdit.setText(user)
        self.lineEdit_2.setFocus()

    def login(self):
        LOGGER.debug('登陆')
        user = self.lineEdit.text().strip()
        pwd = self.lineEdit_2.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, '警告', '请填写完整！')
            return
        if not self.checkBox.isChecked():
            QMessageBox.warning(self, '警告', '请勾选服务协议！')
            return
        request_dic = RequestData.login_dic(user, pwd)
        response_dic = self.get(request_dic)
        if not response_dic:  # 重连成功
            return
        if response_dic.get('code') != 200:
            QMessageBox.about(self, '提示', response_dic.get('msg'))
            return

        self.client.user = user
        self.client.token = response_dic.get('token')
        notice = response_dic.get('notice')
        users = response_dic.get('users')
        # 打开聊天窗口，关闭登陆窗口
        self.chat_window = ChatWindow(self, notice, users)
        self.chat_window.show()
        self.close()

    def open_register_page(self):
        LOGGER.debug('打开注册页面')
        self.stackedWidget.setCurrentIndex(1)

    def open_login_page(self):
        LOGGER.debug('打开登陆页面')
        self.stackedWidget.setCurrentIndex(0)

    def protocol(self):
        LOGGER.debug('查看协议')
        QMessageBox.about(self, '服务协议', '此程序仅供学习使用！')

    def test(self):
        if LEVEL == 'DEBUG':
            self.lineEdit.setText('anlong')
            self.lineEdit_2.setText('123')
            self.checkBox.setChecked(True)


class ChatWindow(ChatUiMixin, QWidget):
    _translate = QCoreApplication.translate

    def __init__(self, login_window, notice, users):
        super().__init__()
        self.client = login_window.client
        self.login_window = login_window
        self.setupUi(self)
        self.tip_label = QLabel()
        self.tip_label.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # 隐藏边框
        self.tip_label.setWindowModality(Qt.WindowModality.ApplicationModal)  # 模态窗口
        self.tip_label.setStyleSheet("background-color: gray")

        self.label.close()
        self.textBrowser.clear()
        self.textEdit.clear()
        self.textEdit_2.setText(notice)
        self.set_online_users(users)

        self.request = queue.Queue()

        self.textEdit.drop_event.connect(self.confirm_send)
        self.textBrowser.anchorClicked.connect(self.open_url)

        self.route_mode = {
            'reconnect': self.reconnect_res,
            'broadcast': self.broadcast_res,
            'chat': self.chat_res,
            'file': self.file_res
        }
        self.singal_route = {
            'show_tip': self.show_tip,
            'close_tip': self.tip_label.close,
            'over': self.over
        }

        # pytz, dateutil, zoneinfo(python3.9)....
        self.last_time = datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc).astimezone().replace(tzinfo=None)

        self.my_thread = MyThread(self.client)
        self.my_thread.reconnected.connect(self.t_signal)
        self.my_thread.received.connect(self.dic_handle)
        self.my_thread.start()

        self.send_thread = MyThread(self.client, self.request)
        self.send_thread.send_success.connect(self.send_success)
        self.send_thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_broadcast)
        self.textEdit.returnPressed.connect(self.send_msg)

        self.textBrowser.setViewportMargins(QMargins(0, 0, 8, 0))

    def send_success(self, request_dic):
        self.append_time(request_dic.get('time'))
        if request_dic.get('mode') == REQUEST_FILE:
            self.show_file(request_dic, 'right')
            return
        self.textEdit.setText('')
        msg = request_dic.get('msg')
        self.show_msg('我', msg, 'right')

    @reconnect
    def put(self, request_dic):
        self.client.send_data(request_dic)
        return True

    @staticmethod
    def open_url(q_url):
        system_name = os.name
        if system_name == 'posix':
            os.system('open "{}"'.format(q_url.toLocalFile()))
        elif system_name == 'nt':
            os.system('start {}'.format(q_url.toLocalFile()))

    @staticmethod
    def get_icon(url):
        icon_path = os.path.join(IMG_DIR, '{}.png'.format(url.split('.')[-1]))
        if os.path.isfile(icon_path):
            return icon_path

        file_info = QFileInfo(url)
        file_icon = QFileIconProvider().icon(file_info)

        file_icon.pixmap(200).save(icon_path)
        return icon_path

    def confirm_send(self, urls):
        files_info = '\n'
        for url in urls:
            file_name = os.path.basename(url)
            file_size = byte_to_human(os.path.getsize(url))
            files_info = '{}{} {}\n'.format(files_info, file_name, file_size)
        files_info = '{}\n是否发送？'.format(files_info)
        res = QMessageBox.question(self, '发送文件', files_info,
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.No:
            return
        # 发送文件数据
        self.send_files(urls)

    def send_files(self, urls):
        for url in urls:
            request_dic = RequestData.file_dic(self.client.user, url, self.client.token)
            self.request.put(request_dic)

    def show_msg(self, user, msg, align):
        self.cursor_end()
        self.textBrowser.insertHtml(f"""
                <tr style="text-align:{align}">
                <p>
                <a style="color:{USER_COLOR}">{user}</a>
                <br>
                <a style="color:{MSG_COLOR}">{msg}</a>

                </p>
                </tr>
                """)
        LOGGER.info('{}说：{}'.format(user, msg))
        self.cursor_end()

    def send_msg(self):
        msg = self.textEdit.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, '警告', '不能发空')
            return
        request_dic = RequestData.chat_dic(self.client.user, msg, self.client.token)
        self.request.put(request_dic)

    def dic_handle(self, response_dic):
        fn = self.route_mode.get(response_dic.get('mode'))
        fn(response_dic)

    def append_time(self, local_time):
        if (local_time - self.last_time).total_seconds() > INTERVAL:
            cursor = self.textBrowser.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.textBrowser.setTextCursor(cursor)
            self.textBrowser.insertHtml(f"""
                            <tr style="text-align:center">
                            <p>
                            <a style="color:{USER_COLOR}">{local_time}</a>
                            </p>
                            </tr>
                            """)
        self.last_time = local_time

    def cursor_end(self):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.textBrowser.setTextCursor(cursor)

    def show_file(self, response_dic, align):
        self.cursor_end()
        user = response_dic.get('user')
        url = response_dic.get('file_path')
        html = """
                                        <tr style="text-align:{}">
                                        <p>
                                        <a style="color:{}">{}</a>
                                        <br>
                                        <a href="file://{}">
                                        <img src="{}" width={}>
                                        </a>
                                        {}
                                        </p>
                                        </tr>
                                        """

        if url.split('.')[-1] in IMG_TYPES:
            # 图片展示
            img_width = QImage(url).width()
            if img_width > 200:
                img_width = 200
            self.textBrowser.insertHtml(html.format(align, USER_COLOR, user, url, url, img_width, ''))
        else:
            # 文件展示
            icon_path = self.get_icon(url)
            file_info_html = """
                                    <br>
                                    <a href="file://{}">【打开文件夹】</a>
                                    <a href="file://{}">{} ({})</a>
                                """
            file_dir = os.path.dirname(url)
            file_name = response_dic.get('file_name')
            file_size = byte_to_human(response_dic.get('file_size'))
            self.textBrowser.insertHtml(html.format(
                align,
                USER_COLOR,
                user,
                url,
                icon_path,
                100,
                file_info_html.format(file_dir, url, file_name, file_size)))

        LOGGER.info('{}发送了文件：{}'.format(user, url))
        self.cursor_end()

    def file_res(self, response_dic, *args, **kwargs):
        utc_time = response_dic.get('time')
        local_time = utc_time.astimezone().replace(tzinfo=None)
        self.append_time(local_time)
        self.show_file(response_dic, 'left')

    def chat_res(self, response_dic, *args, **kwargs):
        user = response_dic.get('user')
        msg = response_dic.get('msg')
        utc_time = response_dic.get('time')
        local_time = utc_time.astimezone().replace(tzinfo=None)
        self.append_time(local_time)
        self.show_msg(user, msg, 'left')

    def reconnect_res(self, response_dic, *args, **kwargs):
        code = response_dic.get('code')
        if code != 200:
            QMessageBox.warning(self, '提示', '{}\n状态码：{}'.format(
                response_dic.get('msg'), code
            ))
            self.login_window.show()
            self.close()
            return

        users = response_dic.get('users')
        self.set_online_users(users)

    def close_broadcast(self):
        # 隐藏广播标签
        self.label.close()
        self.timer.stop()

    def broadcast_res(self, response_dic, *args, **kwargs):
        user = response_dic.get('user')
        if response_dic.get('status') == REQUEST_ONLINE:
            if self.listWidget.findItems(user, Qt.MatchFlag.MatchExactly):
                return

            item = QListWidgetItem()
            self.listWidget.addItem(item)
            if user == self.client.user:
                user = '我'
            item.setText(self._translate("Form", user))

            self.label_3.setText('在线用户数：{}'.format(self.listWidget.count()))

            self.label.show()
            self.label.setText('{} 进入了聊天室'.format(user))
        else:
            """
            QtCore.Qt.MatchFlag.MatchContains：表示在项中查找包含指定文本的任何部分的项
            QtCore.Qt.MatchFlag.MatchExactly：仅匹配与指定文本完全相同的项
            QtCore.Qt.MatchFlag.MatchStartsWith：仅匹配以指定文本开头的项
            QtCore.Qt.MatchFlag.MatchEndsWith：仅匹配以指定文本结尾的项
            """
            item = self.listWidget.findItems(user, Qt.MatchFlag.MatchExactly)[0]
            self.listWidget.takeItem(self.listWidget.row(item))
            self.label_3.setText('在线用户数：{}'.format(self.listWidget.count()))

            self.label.show()
            self.label.setText('{} 离开了聊天室'.format(user))
        self.timer.start(5000)

    def set_online_users(self, users):
        self.listWidget.clear()
        self.label_3.setText('在线用户数：{}'.format(len(users)))
        for user in users:
            item = QListWidgetItem()
            self.listWidget.addItem(item)
            if user == self.client.user:
                user = '我'
            item.setText(self._translate("Form", user))

    def t_signal(self, s):
        self.singal_route.get(s)()

    def show_tip(self):
        self.tip_label.setText('连接断开，正在重连...')
        self.tip_label.adjustSize()
        self.tip_label.setFixedSize(self.tip_label.size())
        self.tip_label.show()

        x = self.geometry().center().x()
        y = self.geometry().center().y()
        self.tip_label.move(x - self.tip_label.width() / 2, y - self.tip_label.height() / 2)

    def over(self):
        QMessageBox.warning(self, '提示', '连接服务器失败，即将关闭程序')
        exit()


class MyThread(QThread):
    reconnected = pyqtSignal(str)
    received = pyqtSignal(dict)
    send_success = pyqtSignal(dict)

    def __init__(self, client, request_q=None):
        self.client = client
        self.request_q = request_q
        super().__init__()

    def run(self):
        if self.request_q:
            self.loop_send()
            return
        self.loop_recv()

    @reconnect_t
    def get(self):
        return self.client.recv_data()

    @reconnect_t
    def put(self, dic):
        self.client.send_data(dic)
        return True

    def loop_recv(self):
        num = 0
        while True:
            response_dic = self.get()
            if not response_dic:
                # 重连成功，发重连请求更新数据
                while True:
                    request_dic = RequestData.reconnect_dic(self.client.user, self.client.token)
                    if not self.put(request_dic):
                        continue
                    LOGGER.info('重连字典发送成功')
                    num += 1
                    if num > 3:
                        self.reconnected.emit('over')
                        return
                    break
                continue
            num = 0
            self.received.emit(response_dic)

    def loop_send(self):
        num = 0
        while True:
            request_dic = self.request_q.get()
            url = request_dic.get('file_path')
            if not self.put(request_dic):
                # 重连成功，发重连请求更新数据
                while True:
                    request_dic = RequestData.reconnect_dic(self.client.user, self.client.token)
                    if not self.put(request_dic):
                        continue
                    LOGGER.info('重连字典发送成功')
                    num += 1
                    if num > 3:
                        self.reconnected.emit('over')
                        return
                    break
                continue
            num = 0

            # 发送成功
            request_dic['file_path'] = url
            self.send_success.emit(request_dic)

def run():
    import sys
    # 连接服务器
    with MySocket(HOST, PORT) as client:
        # 展示登陆界面
        app = QApplication(sys.argv)
        login_window = LoginWindow(client)
        login_window.show()
        sys.exit(app.exec())
