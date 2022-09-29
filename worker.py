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
        self.mux = threading.Semaphore(1)  # 对working_thread互斥访问
        self.working_thread = []  # 活跃进程列表

    # 检查是否有空闲线程，没有则释放
    def check(self):
        self.mux.acquire()
        working_thread_cnt = len(self.working_thread)

        if working_thread_cnt == self.max_connection:
            self.mux.acquire()
            thread = self.working_thread.pop(0)  # 释放最早的
            self.mux.release()
            thread.end()
            # thread.start()

        print("now working thread: " + str(working_thread_cnt) +
              " ; free thread: " +
              str(self.max_connection - working_thread_cnt) +
              " ; now waiting request: " + str(tasks.qsize()))

        self.mux.release()

    def run(self):
        # print(self.max_connection)
        for _ in range(self.max_connection):
            Worker(self.log_name, self.mux, self.working_thread).start()


class Worker(threading.Thread):
    def __init__(self, _log_name, mux, working_thread):
        super().__init__()

        self.log_name = _log_name
        self.mux = mux  # 对working_thread互斥访问
        self.working_thread = working_thread  # 所属活跃进程列表
        self.msg = bytes()
        self.status_code = -1

        self.file_handle = None
        self.socket: socket.socket | None = None
        self.proc = None

        self.stopped = 0  # 控制线程停止，执行时定期检查stop，为1则退出
        self.daemon = True

    def end(self):  # stop置1，强行终止(重启)
        self.stopped = 1
        # self.join()
        # self.release()

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
            file_suffix = file_name.split('.')[-1].encode()
            content = b"HTTP/1.1 200 OK\r\nContent-Type: text/" + \
                      file_suffix + b";charset=utf-8\r\n\r\n"

            self.status_code = 200
        else:
            file_name = "404.html"
            content = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html;charset=utf-8\r\n\r\n"

            self.status_code = 404

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

    def post(self, file_name):
        if self.stopped:
            return
        command = 'python ' + file_name + ' "' + self.msg[-1] + '"'
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

        if self.proc.poll() == 2:  # 2子进程不存在
            content = b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html;charset=utf-8\r\n\r\n"
            self.file_handle = open("403.html", "rb")
            for line in self.file_handle:
                content += line

            self.status_code = 403
        else:
            content = b"HTTP/1.1 200 OK\r\nContent-Type: text/html;charset=utf-8\r\n\r\n"

            # content += self.proc.stdout.read()
            name, _ = os.path.splitext(file_name)
            file_name = name + '.html'
            self.file_handle = open(file_name, "rb")
            for line in self.file_handle:
                content += line

            file_size = os.path.getsize(file_name)
            self.status_code = 200

        if self.stopped:
            return

        self.socket.sendall(content)

        self.write_log(file_size)

    # 日志书写（文件大小）
    def write_log(self, file_size):
        content = self.msg[1].split(":")[1].replace(" ", "")
        content += f'--[' \
                   f'{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}_' \
                   f'{time.localtime().tm_hour}.{time.localtime().tm_min}.{time.localtime().tm_sec}' \
                   f']'
        content += f' {self.msg[0].split("/")[0].replace(" ", "")} {self.msg[0].split(" ")[1].replace(" ", "")} '
        content += f'{file_size} {self.status_code} '
        for each in self.msg:
            if each.split(" ")[0] == "Referer:":
                content = content + each.split(" ")[1].replace(" ", "")

        content += "\n"
        with open(self.log_name, "a") as f:
            f.write(content)

    def run(self):
        while True:
            self.stopped = 0
            full.acquire()  # 等待连接

            tasks_mux.acquire()
            self.socket = tasks.get()
            tasks_mux.release()

            self.mux.acquire()
            self.working_thread.append(self)
            self.mux.release()

            if self.stopped:
                self.release()
                continue

            self.msg = bytes()
            while True:
                message = self.socket.recv(4096)  # a power of 2
                # # nonblocking mode: timeout before recv or no available msg
                # if message == -1:
                #    break
                self.msg += message
                if len(message) < 4096:
                    break

            self.msg = self.msg.decode("utf-8").splitlines()
            # print(self.msg)

            if self.stopped:
                self.release()
                continue
            elif self.msg:
                key_mes = self.msg[0].split()
                # [0] get/post medthod [1]req doc [2]http version
            else:
                print("error when reading message:msg empty")
                continue

            if len(key_mes) <= 1:
                print("error when reading message:msg empty")
                continue

            if self.stopped:
                self.release()
                continue
            file_name = "index.html"
            if key_mes[1] != "/":
                file_name = key_mes[1][1:]

            if self.stopped:
                self.release()
                continue
            try:
                match key_mes[0]:
                    case 'GET':
                        self.get(file_name)
                    case 'POST':
                        self.post(file_name)
                    case 'HEAD':
                        self.get(file_name, True)
                    case _:
                        content = b'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n'
                        self.socket.sendall(content)
            except Exception as e:
                print("reason:", e)

            if self.stopped:  # 其它线程停止的，已经被移除出工作线程队列
                self.release()
            else:  # 继续等待连接
                self.release()
                self.mux.acquire()
                self.working_thread.remove(self)
                self.mux.release()
