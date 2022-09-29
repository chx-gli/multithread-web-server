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


MAX_CONN = 256
with ThreadPoolExecutor(max_workers=MAX_CONN) as tp:
    tasks = []
    task_append = tasks.append
    for i in range(MAX_CONN):
        task_append(tp.submit(head_test))

    success, failure = 0, 0
    for each in tasks:
        match each.result():
            case 200:
                success += 1
            case _:
                failure += 1
    print(f'Success: {success}, failure: {failure}, success rate = {100 * success / (success + failure):.2f}%')
