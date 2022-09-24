# -*- coding: utf-8 -*-
import socket
# from concurrent.futures import ThreadPoolExecutor
# from task import task
import time
from semas import full,tasks_mux,tasks
from worker import ThreadPool


PORT = 9000

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

tp = ThreadPool(log_name)

#监听循环
while True:
    try:
        client, addr = server_socket.accept()
        print("recv: ", client.getpeername(), client.getsockname())
        #tp.submit(task(client, log_name))

        # produce
        tp.check()
        tasks_mux.acquire()
        tasks.put(client)
        tasks_mux.release()
        full.release()


    except socket.timeout:
        print("main server timeout")
        # break 取消timeout试试
