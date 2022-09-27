import os.path
import socket
import sys

import time
from semas import full, tasks_mux, tasks
from worker import ThreadPool

MAX_CONNECTION = 10
PORT = 9000

if not os.path.isdir('log'):
    os.mkdir('log')

# 命令行输入最大连接数
if len(sys.argv) > 1:
    try:
        MAX_CONNECTION = eval(sys.argv[1])
    except Exception as e:
        print(type(e), e, file=sys.stderr)

# socket listen
listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_name = socket.gethostbyname(host_name)
address = ("0.0.0.0", PORT)
listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening_socket.bind(address)
listening_socket.settimeout(10)  # 超时模式，操作系统级别非阻塞模式
listening_socket.listen(5)  # 拒绝连接前可以挂起的最大连接数

print(f'http://127.0.0.1:{PORT}')

# create log
cur_time = time.localtime()
log_name = f'log/' \
           f'{cur_time.tm_year}-{cur_time.tm_mon}-{cur_time.tm_mday}_' \
           f'{cur_time.tm_hour}.{cur_time.tm_min}.{cur_time.tm_sec}.txt'

tp = ThreadPool(log_name, MAX_CONNECTION)
tp.start()

# 监听循环
while True:
    try:
        clientSocket, addr = listening_socket.accept()  # cleint是阻塞模式
        print(f'Receive request from {clientSocket.getpeername()}.')

        # produce
        tp.check()
        tasks_mux.acquire()

        tasks.put(clientSocket)
        tasks_mux.release()
        full.release()
    except socket.timeout:
        print("socket timeout")
