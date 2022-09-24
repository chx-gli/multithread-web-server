# -*- coding: utf-8 -*-
import socket
<<<<<<< HEAD
import sys
=======
from worker import tasks, working_thread, worker, sema
import threading
>>>>>>> 65e97fddb6e1896c97b301630d89cdf620c3b80b
import time
from semas import full,tasks_mux,tasks
from worker import ThreadPool


MAX_CONNECTION = 10
PORT = 9000

#命令行输入最大连接数
if len(sys.argv) > 1:
    if eval(sys.argv[1]) > 0:
        MAX_CONNECTION = eval(sys.argv[1])

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


<<<<<<< HEAD
# create log
cur_time = time.localtime()
log_name = "log/" + str(cur_time.tm_year) + "-" + str(
    cur_time.tm_mon) + "-" + str(cur_time.tm_mday) + "-" + str(
        cur_time.tm_hour) + "-" + str(cur_time.tm_min) + "-" + str(
            cur_time.tm_sec) + ".txt"

tp = ThreadPool(log_name,MAX_CONNECTION)
=======
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
                if (len(working_thread) == MAX_CONNECTION and
                        MAX_CONNECTION != 0 and
                        (not tasks.empty())):
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
>>>>>>> 65e97fddb6e1896c97b301630d89cdf620c3b80b

#监听循环
while True:
    try:
        client, addr = server_socket.accept()
        print("recv: ", client.getpeername(), client.getsockname())
<<<<<<< HEAD
        #tp.submit(task(client, log_name))

        # produce
        tp.check()
        tasks_mux.acquire()
=======
>>>>>>> 65e97fddb6e1896c97b301630d89cdf620c3b80b
        tasks.put(client)
        tasks_mux.release()
        full.release()


    except socket.timeout:
        print("main server timeout")
        # break 取消timeout试试
