import socket
import sys

import time
from semas import full, tasks_mux, tasks
from worker import ThreadPool

MAX_CONNECTION = 10
PORT = 9000

# 命令行输入最大连接数
if len(sys.argv) > 1:
    try:
        MAX_CONNECTION = eval(sys.argv[1])
    except Exception as e:
        print(type(e), e, file=sys.stderr)

# socket listen
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_name = socket.gethostbyname(host_name)
address = ("0.0.0.0", PORT)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(address)
server_socket.settimeout(60)  # todo param
server_socket.listen(2)  # todo param

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
        client, addr = server_socket.accept()
        # client.getsockname() -> ('127.0.0.1', 9000)
        print(f'Receive request from {client.getpeername()}.')

        # produce
        tp.check()
        tasks_mux.acquire()

        tasks.put(client)
        tasks_mux.release()
        full.release()
    except socket.timeout:
        print("main server timeout")
