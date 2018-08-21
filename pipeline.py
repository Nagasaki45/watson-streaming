import threading

from six.moves import queue


class Node(threading.Thread):
    def __init__(self):
        super(Node, self).__init__()
        self._input = queue.Queue()
        self._output = queue.Queue()  # In case nothing is connected

    def generate(self):
        pass

    def consume(self, item):
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    def connect(self, other_process):
        self._output = other_process._input

    def put(self, item):
        self._output.put(item)

    def stop(self):
        self._input.put(None)

    def run(self):
        self.enter()
        try:
            while True:
                if not self._input.empty():
                    item = self._input.get()
                    if item is None:
                        break
                    self.consume(item)
                self.generate()
        finally:
            self.exit()


def connect(nodes):
    for a, b in zip(nodes[:-1], nodes[1:]):
        a.connect(b)


def start(nodes):
    for node in nodes:
        node.start()


def stop(nodes):
    for node in nodes:
        node.stop()
