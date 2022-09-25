import threading
import subprocess
import os
import time
from semas import full,tasks_mux, tasks

mux = threading.Semaphore(1) #对working_thread互斥访问
working_thread = list()  # 活跃进程列表

class ThreadPool(threading.Thread):
    def __init__(self, _log_name,MAX_CONNECTION):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.log_name = _log_name
        self.MAX_CONNECTION = MAX_CONNECTION
        self.start()

    #检查是否有空闲线程，没有则释放
    def check(self):
        mux.acquire()
        working_thread_cnt = len(working_thread)
        
        if working_thread_cnt == self.MAX_CONNECTION:
            thread = working_thread.pop(0) #释放最早的
            thread.restart()
        
        print("now working thread: " + str(working_thread_cnt) +
        " ; free thread: " +
        str(self.MAX_CONNECTION - working_thread_cnt) +
        " ; now waiting request: " + str(tasks.qsize()))

        mux.release()

    def run(self):
        for i in range(self.MAX_CONNECTION):
            worker(self.log_name)
        # while True:
        #     for i in range(10):
        #     if (len(working_thread) == MAX_CONNECTION and (not tasks.empty())):
        #         print("shutdown")
        #         working_thread[0].restart()
        #     sema.acquire(timeout=1)
        #     time.sleep(1)
        #     working_thread_cnt = len(working_thread)
        #     tasks_mux.acquire()

        #     tasks_mux.release()


class worker(threading.Thread):
    def __init__(self, log_name):
        self.log_name = log_name
        self.msg = None
        self.status_code = -1

        self.file_handle = None
        self.socket = None
        self.proc = None

        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()



    def restart(self):
        if (self.file_handle != None):
            self.file_handle.close()
            self.file_handle = None
        if (self.socket != None):
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except Exception as e:
                print("socket error:", e)
            self.socket = None
        if (self.proc != None and self.proc.poll() != None):
            self.proc.kill()
            self.proc = None

    def get(self, file_name, is_head=False):
        if (os.path.isfile(file_name)):
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
        self.socket.sendall(content)

        file_size = 0

        if not is_head:
            self.file_handle = open(file_name, "rb")
            for line in self.file_handle:
                self.socket.sendall(line)

            file_size = os.path.getsize(file_name)

        self.write_log(file_size)

    def post(self, file_name, args):
        command = 'python ' + file_name + ' "' + args + '" "' + self.socket.getsockname(
        )[0] + '" "' + str(self.socket.getsockname()[1]) + '"'
        print(command)
        self.proc = subprocess.Popen(command,
                                     shell=True,
                                     stdout=subprocess.PIPE)
        self.proc.wait()

        file_size = 0

        if (self.proc.poll() == 2):  # 文件不存在时返回值为2
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
        while(True):
            full.acquire()#等待连接

            tasks_mux.acquire()
            self.socket = tasks.get()
            tasks_mux.release()

            mux.acquire()
            working_thread.append(self)
            mux.release()

            message = self.socket.recv(8000).decode("utf-8")
            message = message.splitlines()

            self.msg = message

            if (message):
                key_mes = message[0].split()
            else:
                self.restart()
                continue
            if (len(key_mes) <= 1):
                self.restart()
                continue
            file_name = "index.html"
            if (key_mes[1] != "/"):
                file_name = key_mes[1][1:]

            try:
                if (key_mes[0] == 'GET'):
                    self.get(file_name)
                elif (key_mes[0] == 'POST'):
                    self.post(file_name, message[-1])
                elif (key_mes[0] == 'HEAD'):  
                    self.get(file_name, True)
                else:
                    content = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n"
                    self.socket.sendall(content)
            except Exception as e:
                print("reason:", e)  # read a closed file
            self.restart()
            mux.acquire()
            working_thread.remove(self)
            mux.release()
