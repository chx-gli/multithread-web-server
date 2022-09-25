import socket
import threading
import subprocess
import os
import time
from semas import full, tasks_mux, tasks

mux = threading.Semaphore(1)  # 对working_thread互斥访问
working_thread = []  # 活跃进程列表


class ThreadPool(threading.Thread):
    def __init__(self, _log_name, max_connection):
        super().__init__()
        self.daemon = True
        self.log_name = _log_name
        self.max_connection = max_connection

    # 检查是否有空闲线程，没有则释放
    def check(self):
        mux.acquire()
        working_thread_cnt = len(working_thread)

        if working_thread_cnt == self.max_connection:
            thread = working_thread.pop(0)  # 释放最早的
            thread.end()
            thread.start()

        print("now working thread: " + str(working_thread_cnt) +
              " ; free thread: " +
              str(self.max_connection - working_thread_cnt) +
              " ; now waiting request: " + str(tasks.qsize()))

        mux.release()

    def run(self):
        for i in range(self.max_connection):
            Worker(self.log_name).start()


class Worker(threading.Thread):
    def __init__(self, _log_name):
        super().__init__()

        self.log_name = _log_name
        self.msg = None
        self.status_code = -1

        self.file_handle = None
        self.socket: socket.socket | None = None
        self.proc = None

        self.stopped = 0  # 控制线程停止，执行时定期检查stop，为1则退出
        self.daemon = True

    def end(self):  # stop置1并释放资源，强行终止
        self.stopped = 1
        self.join()
        self.release()

    def release(self):  # 释放资源
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None
        if self.socket is not None:
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except Exception as e:
                print("socket error:", e)
            self.socket = None
        if self.proc is not None and self.proc.poll() is not None:
            self.proc.kill()
            self.proc = None

    def get(self, file_name, is_head=False):
        if self.stopped:
            return
        if os.path.isfile(file_name):
            file_suffix = file_name.split('.')
            file_suffix = file_suffix[-1].encode()
            content = b"HTTP/1.1 200 OK\r\nContent-Type: text/" + \
                      file_suffix + b";charset=utf-8\r\n"

            self.status_code = 200
        else:
            content = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html;charset=utf-8\r\n"
            file_name = "404.html"

            self.status_code = 404
        content += b'\r\n'

        if self.stopped:
            return
        self.socket.sendall(content)

        file_size = 0

        if not is_head:
            self.file_handle = open(file_name, "rb")
            for line in self.file_handle:
                self.socket.sendall(line)

            file_size = os.path.getsize(file_name)

        self.write_log(file_size)

    def post(self, file_name, args):
        if self.stopped:
            return
        command = 'python ' + file_name + ' "' + args + '" "' + self.socket.getsockname(
        )[0] + '" "' + str(self.socket.getsockname()[1]) + '"'
        print(command)
        if self.stopped:
            return
        self.proc = subprocess.Popen(command,
                                     shell=True,
                                     stdout=subprocess.PIPE)
        self.proc.wait()

        if self.stopped:
            return

        file_size = 0

        if self.proc.poll() == 2:  # 文件不存在时返回值为2
            content = b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html;charset=utf-8\r\n"
            page = b''
            self.file_handle = open("403.html", "rb")
            for line in self.file_handle:
                page += line
            content += b'\r\n'
            content += page

            self.status_code = 403
        else:
            content = b"HTTP/1.1 200 OK\r\nContent-Type: text/html;charset=utf-8\r\n"
            content += self.proc.stdout.read()

            file_size = os.path.getsize(file_name)
            self.status_code = 200

        if self.stopped:
            return

        self.socket.sendall(content)

        self.write_log(file_size)

    # 日志书写（文件大小）
    def write_log(self, file_size):
        content = self.msg[1].split(":")[1].replace(" ", "")
        content = content + "--"
        content = content + "[" + str(time.localtime().tm_year) + "-" + str(
            time.localtime().tm_mon) + "-" + str(
            time.localtime().tm_mday) + "-" + str(
            time.localtime().tm_hour) + "-" + str(
            time.localtime().tm_min) + "-" + str(
            time.localtime().tm_sec) + "]"
        content = content + " " + self.msg[0].split("/")[0].replace(" ",
                                                                    "") + " "
        content = content + " " + self.msg[0].split(" ")[1].replace(" ",
                                                                    "") + " "
        content = content + str(file_size) + " "
        content = content + str(self.status_code) + " "
        for i in self.msg:
            # print(i)
            # print(i.split(" ")[0])
            if (i.split(" ")[0] == "Referer:"):
                content = content + i.split(" ")[1].replace(" ", "")

        content = content + "\n"
        with open(self.log_name, "a") as f:
            f.write(content)

    def run(self):
        self.stopped = 0
        while (True):
            full.acquire()  # 等待连接

            tasks_mux.acquire()
            self.socket = tasks.get()
            tasks_mux.release()

            mux.acquire()
            working_thread.append(self)
            mux.release()

            if self.stopped:
                break

            message = self.socket.recv(8000).decode("utf-8")
            message = message.splitlines()

            self.msg = message

            if self.stopped:
                break
            elif self.msg:
                key_mes = self.msg[0].split()
            else:
                print("error when reading message:msg empty")
                continue

            if len(key_mes) <= 1:
                print("error when reading message:msg empty")
                continue

            if self.stopped:
                break
            file_name = "index.html"
            if key_mes[1] != "/":
                file_name = key_mes[1][1:]

            if self.stopped:
                break
            try:
                match key_mes[0]:
                    case 'GET':
                        self.get(file_name)
                    case 'POST':
                        self.post(file_name, message[-1])
                    case 'HEAD':
                        self.get(file_name, True)
                    case _:
                        content = b'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n'
                        self.socket.sendall(content)
            except Exception as e:
                print("reason:", e)

            if self.stopped:
                break
            else:  # 继续等待连接
                self.release()
                mux.acquire()
                working_thread.remove(self)
                mux.release()
