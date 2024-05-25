from serial_conn import SerialThread
from ui import UIThread
import queue, threading

if __name__ == '__main__':
    queue = queue.Queue()
    serial_thread = threading.Thread(target=SerialThread().run, args=(queue,), daemon=True)
    ui_thread = threading.Thread(target=UIThread().run, args=(queue,), daemon=True)
    serial_thread.start()
    ui_thread.start()
    try:
        while True:
            print(end="")
    except KeyboardInterrupt:
        print()
        queue.put('stop')
        serial_thread.join()
        ui_thread.join()


    