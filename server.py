# -*- coding: utf-8 -*-
import socket
from worker import tasks, working_thread, worker,sema
import threading
import time

MAX_CONNECTION = 5  #
PORT = 9000

# Main thread
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_name = socket.gethostbyname(host_name)
address = ("0.0.0.0", PORT)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(address)
server_socket.settimeout(60)
server_socket.listen(2)

print(host_name + ':' + str(PORT))


class ThreadPool(threading.Thread):
    def __init__(self, _log_name):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.log_name = _log_name
        self.start()

    def run(self):
        for i in range(MAX_CONNECTION):
            worker(self.log_name)
        while True:
            for i in range(10):
                # print(len(working_thread), tasks.empty())
                if (len(working_thread) == MAX_CONNECTION
                        and MAX_CONNECTION != 0 and (not tasks.empty())):
                    print("shutdown")
                    working_thread[0].restart()
                # time.sleep(0.1)
            sema.acquire(timeout=1)
            
            working_thread_cnt = len(working_thread)
            print("now working thread: " + str(working_thread_cnt) +
                  " ; free thread: " +
                  str(MAX_CONNECTION - working_thread_cnt) +
                  " ; now waiting request: " + str(tasks.qsize()))


# 每一次运行都创建一个日志文件
now_time = time.localtime()
log_name = "log/" + str(now_time.tm_year) + "-" + str(
    now_time.tm_mon) + "-" + str(now_time.tm_mday) + "-" + str(
        now_time.tm_hour) + "-" + str(now_time.tm_min) + "-" + str(
            now_time.tm_sec) + ".txt"

ThreadPool(log_name)

while True:
    try:
        client, addr = server_socket.accept()
        print("recv: ",client.getpeername(),client.getsockname())
        tasks.put(client)
        # ！！！！ qsize不是阻塞的 当多个请求同时到达qsize不是当前的值
        # if (working_thread.qsize() == MAX_CONNECTION):
        #     working_thread.get().restart()

    except socket.timeout:
        print("main server timeout")
        # break 取消timeout试试
