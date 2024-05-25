class DataProcessor:
    SPEED = 150
    def __init__(self, queues):
        print("dataprocessor init")
        self.queues = queues

    def write_speed(self, speed1, speed2):
        try:
            self.queues.send_input(f'send: {speed1},{speed2}')
        except Exception as e:
            print(e.message)
        pass

    def forward(self):
        self.write_speed(self.SPEED, self.SPEED)
    def right(self):
        pass
    def left(self):
        pass
    def back(self):
        pass
    def stop(self):
        self.write_speed(0, 0)

    def loop(self, millis, sensor_data):
        fl = sensor_data[0]
        cl = sensor_data[1]
        cc = sensor_data[2]
        cr = sensor_data[3]
        fr = sensor_data[4]

        if fr == 1:
            self.left()
        elif cc == 0:
            self.back()
        elif cl == 1:
            self.right()
        elif cr == 1:
            self.left()
        self.write_speed(109, 33)
        print(millis, sensor_data)
    


data_processor = None

def process_data(queues, millis, sensor_data):
    global data_processor
    if data_processor is None:
        data_processor = DataProcessor(queues)
    data_processor.loop(millis, sensor_data)
    pass
