import requests
from concurrent.futures import ThreadPoolExecutor


def head_test() -> int:
    try:
        r = requests.head('http://127.0.0.1:9000', timeout=1)
        r.raise_for_status()
        return r.status_code
    except Exception as e:
        print(e)
        return -1


with ThreadPoolExecutor(max_workers=64) as tp:
    tasks = []
    task_append = tasks.append
    for i in range(64):
        task_append(tp.submit(head_test))

    for each in tasks:
        print(each.result())
