import queue
class IOQueues:
    def __init__(self):
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

    def send_input(self, message):
        self.input_queue.put(message)

    def get_input(self):
        return self.input_queue.get_nowait()

    def send_output(self, message):
        self.output_queue.put(message)

    def get_output(self):
        return self.output_queue.get_nowait()

    @property
    def input_waiting(self):
        return not self.input_queue.empty()
    @property
    def output_waiting(self):
        return not self.output_queue.empty()