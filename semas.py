import threading
from queue import Queue

# empty_mux = threading.Semaphore(1) #对empty的互斥访问
# empt = MAX_CONNECTION #不是信号量，empty不够时不阻塞，而是强行释放一个出来
full = threading.Semaphore(0)
tasks_mux = threading.Semaphore(1)  # 对tasks的互斥访问
tasks = Queue()
