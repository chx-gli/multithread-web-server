# -*- coding: utf-8 -*-
import socket
# from worker import tasks, working_thread, worker, sema
import threading
from concurrent.futures import ThreadPoolExecutor
from task import task
import time

MAX_CONNECTION = 10  #
PORT = 9000


# class ThreadPool(threading.Thread):
#     def __init__(self, _log_name):
#         threading.Thread.__init__(self)
#         self.setDaemon(True)
#         self.log_name = _log_name
#         self.start()

#     def run(self):
#         for i in range(MAX_CONNECTION):
#             worker(self.log_name)
#         while True:
#             # for i in range(10):
#             if (len(working_thread) == MAX_CONNECTION and (not tasks.empty())):
#                 print("shutdown")
#                 working_thread[0].restart()
#             sema.acquire(timeout=1)

#             working_thread_cnt = len(working_thread)
#             print("now working thread: " + str(working_thread_cnt) +
#                   " ; free thread: " +
#                   str(MAX_CONNECTION - working_thread_cnt) +
#                   " ; now waiting request: " + str(tasks.qsize()))


# socket listen
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_name = socket.gethostbyname(host_name)
address = ("0.0.0.0", PORT)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(address)
server_socket.settimeout(60)  # todo param
server_socket.listen(2)  # todo param

print(host_name + ':' + str(PORT))


# create log
cur_time = time.localtime()
log_name = "log/" + str(cur_time.tm_year) + "-" + str(
    cur_time.tm_mon) + "-" + str(cur_time.tm_mday) + "-" + str(
        cur_time.tm_hour) + "-" + str(cur_time.tm_min) + "-" + str(
            cur_time.tm_sec) + ".txt"

# ThreadPool(log_name)

#监听循环
with ThreadPoolExecutor(max_workers= MAX_CONNECTION) as tp:
    while True:
        try:
            client, addr = server_socket.accept()
            print("recv: ", client.getpeername(), client.getsockname())
            tp.submit(task(client, log_name))
            # tasks.put(client)
            # ！！！！ qsize不是阻塞的 当多个请求同时到达qsize不是当前的值
            # if (working_thread.qsize() == MAX_CONNECTION):
            #     working_thread.get().restart()

        except socket.timeout:
            print("main server timeout")
            # break 取消timeout试试
