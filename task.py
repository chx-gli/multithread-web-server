import os
import time
import subprocess


# 日志书写（文件大小）
def write_log(msg, file_size, log_name, status_code):
    content = msg[1].split(":")[1].replace(" ", "")
    content = content + "--"
    content = content + "[" + str(time.localtime().tm_year) + "-" + str(
        time.localtime().tm_mon) + "-" + str(
            time.localtime().tm_mday) + "-" + str(
                time.localtime().tm_hour) + "-" + str(
                    time.localtime().tm_min) + "-" + str(
                        time.localtime().tm_sec) + "]"
    content = content + " " + msg[0].split("/")[0].replace(" ",
                                                           "") + " "
    content = content + " " + msg[0].split(" ")[1].replace(" ",
                                                           "") + " "
    content = content + str(file_size) + " "
    content = content + str(status_code) + " "
    for i in msg:
        # print(i)
        # print(i.split(" ")[0])
        if (i.split(" ")[0] == "Referer:"):
            content = content + i.split(" ")[1].replace(" ", "")

    content = content + "\n"
    with open(log_name, "a") as f:
        f.write(content)


# is_head = true : HEAD
def get(socket, log_name,msg, file_name, is_head=False):
    if (os.path.isfile(file_name)):
        file_suffix = file_name.split('.')
        file_suffix = file_suffix[-1].encode()
        content = b"HTTP/1.1 200 OK\r\nContent-Type: text/" + \
            file_suffix + b";charset=utf-8\r\n"

        status_code = 200
    else:
        content = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html;charset=utf-8\r\n"
        file_name = "404.html"

        status_code = 404
    content += b'\r\n'
    socket.sendall(content)

    file_size = 0

    if not is_head:
        file_handle = open(file_name, "rb")
        for line in file_handle:
            socket.sendall(line)

        file_size = os.path.getsize(file_name)

    write_log(msg,file_size,log_name,status_code)


def post(socket, log_name,msg,file_name, args):
    command = 'python ' + file_name + ' "' + args + '" "' + socket.getsockname(
    )[0] + '" "' + str(socket.getsockname()[1]) + '"'
    proc = subprocess.Popen(command,
                                 shell=True,
                                 stdout=subprocess.PIPE)
    proc.wait()

    file_size = 0

    if (proc.poll() == 2):  # 文件不存在时返回值为2
        content = b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html;charset=utf-8\r\n"
        page = b''
        file_handle = open("403.html", "rb")
        for line in file_handle:
            page += line
        content += b'\r\n'
        content += page

        status_code = 403
    else:
        content = b"HTTP/1.1 200 OK\r\nContent-Type: text/html;charset=utf-8\r\n"
        content += proc.stdout.read()

        file_size = os.path.getsize(file_name)
        status_code = 200
    socket.sendall(content)

    write_log(msg,file_size,log_name,status_code)


def task(clientSocket, log_name):
    message = clientSocket.recv(8000).decode("utf-8")
    message = message.splitlines()

    if (message):
        key_mes = message[0].split()
    else:
        return
    if (len(key_mes) <= 1):
        return

    file_name = "index.html"
    if (key_mes[1] != "/"):
        file_name = key_mes[1][1:]

    try:
        if (key_mes[0] == 'GET'):
            get(clientSocket,log_name,message, file_name)
        elif (key_mes[0] == 'POST'):
            post(clientSocket,log_name,message,file_name, message[-1])
        elif (key_mes[0] == 'HEAD'):
            get(clientSocket,log_name,message,file_name, True)
        else:
            content = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n"
            clientSocket.sendall(content)
    except Exception as e:
        print("reason:", e)  # read a closed file
