import threading
import queue
import time
import serial

class SerialThread:
    def __init__(self):
        self.serial_conn = None
        self.running = True
        self.write_queue = queue.Queue()
        self.read_queue = queue.Queue()
    def read_from_serial(self):
        while self.running:
            if self.serial_conn and self.serial_conn.in_waiting > 0:
                try:
                    data = self.serial_conn.readline().decode('utf-8')
                    if data:
                        self.read_queue.put(data)
                except serial.SerialException as e:
                    self.read_queue.put('(ERROR) '+ str(e))
            time.sleep(0.01)
    def write_to_serial(self):
        while self.running:
            try:
                cmd = self.write_queue.get()
                if self.serial_conn:
                    print("writing")
                    self.serial_conn.write(cmd.encode('utf-8'))
                else: 
                    print("no serial conn")
            except queue.Empty:
                cmd = ""
            time.sleep(0.01)

    def run(self, queues):
        threading.Thread(target=self.read_from_serial).start()
        threading.Thread(target=self.write_to_serial).start()
        print("Serial Thread start")
        while self.running:
            time.sleep(0.01)
            # Pull data from serial port
            try: 
                data = self.read_queue.get_nowait()
            except queue.Empty:
                data = None
            if data:
                queues.send_output(data)


            # Check if there is command to be read
            cmd = ''

            try: 
                if queues.input_waiting:
                    cmd = queues.get_input()
            except queue.Empty:
                    sleep(0.01)

            # Process command

            if cmd == 'stop':
                self.stop()
                break
            if 'disconnect' in cmd:
                if self.serial_conn:
                    self.serial_conn.close()
                    self.serial_conn = None
                    queues.send_output('(INFO) Disconnected')
                else:
                    queues.send_output('(WARNING) Not connected')
            elif 'connect' in cmd:
                if self.serial_conn:
                    queues.send_output('(WARNING) Already connected to port ' + self.serial_conn.port)
                else:
                    port = cmd.split()[1]
                    self.serial_conn = serial.Serial(port, 9600, timeout=0.1)
                    queues.send_output('(INFO) Connected to port ' + port)
            elif 'send' in cmd:
                if self.serial_conn:
                    queues.send_output('(INFO) Sent data')
                    self.write_queue.put(cmd.split(': ')[1])
                else:
                    queues.send_output('(WARNING) Not connected')
            elif cmd == '': pass
            else: 
                queues.send_output("Command not found " + '[' + cmd + ']')


    def stop(self):
        print("bye")
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
