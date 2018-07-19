import os
import time
from multiprocessing import Process, freeze_support


def runner(data):
    cmd = 'C:/Users/Administrator.EBAY-10/venv/Scripts/python ' + os.path.dirname(__file__) + '/amazon.py ' + str(data['index'])
    print(cmd)
    os.system(cmd)
    print("Work done.")


if __name__ == '__main__':
    for val in [{'index': 1}, {'index': 2}, {'index': 3}, {'index': 4}]:
        time.sleep(int(val['index'])*2)
        p = Process(target=runner, args=(val,))
        p.start()

