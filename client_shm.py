from multiprocessing import shared_memory
import pickle
import struct
import threading
from queue import Queue
import time
from typing import Union
import warnings


def mmap_write(mm, msg):
    payload = pickle.dumps(msg)
    payload_size = len(payload)
    buffer = struct.pack('!I', payload_size) + payload
    mm.buf[:4+payload_size] = buffer


def mmap_read(mm, size):
    payload = pickle.loads(mm.buf[4:4 + size])
    mm.buf[:4+size] = bytearray(4 + size)  # Clear the memory after reading
    return payload


class ZMHandler(threading.Thread):

    def __init__(self, publication: dict, subscription: dict, queue, bq,
                 callback=None):
        threading.Thread.__init__(self)
        self.publication = publication
        self.subscription = subscription
        self.queue = queue
        self.bq = bq
        self.callback = callback

    def run(self):
        while True:
            for topic, mm in self.subscription.items():
                payload_size = struct.unpack('!I', mm.buf[:4])[0]
                if payload_size:
                    payload = mmap_read(mm, payload_size)
                    if self.callback:
                        self.callback(topic, payload)
                    else:
                        self.bq.put([topic, payload])
                    continue
            while True:
                if not self.queue.empty():
                    topic, msg = self.queue.get()
                    mm = self.publication[topic]
                    mmap_write(mm, msg)
                else:
                    break


class ZMClient:
    """
    A zero-copy memory-sharing IPC client
    """

    def __init__(self):
        self.queue = Queue()
        self.bq = Queue()
        self.publication = {}
        self.subscription = {}
        self.pub_bg = {}
        self.sub_bg = {}
        self.bg_flag = False

    def add_publication(self, topic: str, msglen: int = 100000):
        self.publication[topic] = shared_memory.SharedMemory(
            name=topic, create=True, size=msglen)

    def add_subscription(self, topic: str, msglen: int = 100000):
        self.subscription[topic] = shared_memory.SharedMemory(
            name=topic, create=False, size=msglen)

    def publish(self, topic, msg, background=False):
        if background:
            self.queue.put([topic, msg])
        else:
            mm = self.publication[topic]
            mmap_write(mm, msg)

    def receive(self, topic, timeout: Union[int, float] = 10,
                background=False):
        """
        Receive messages in either blocking or non-blocking way. Note the
        non-blocking way has to work with the ZMHandler, which means the
        user need to call the execute function prior to this function.
        :param topic: The channel where you want to receive the message.
        :param timeout: How long you want to wait in the blocking way.
        :param background: Default is false. Set it to True if you want to
        have a non-blocking call.
        :return: The unpickled message or a dictionary of topic and message
        pairs.
        """
        if self.bg_flag:
            if not background:
                warnings.warn("Execute in non-blocking mode.", Warning)
            payload_collection = {}
            while True:
                if self.bq.empty():
                    payload = payload_collection if payload_collection else \
                        None
                    break
                else:
                    topic, msg = self.bq.get()
                    payload_collection[topic] = msg
        else:
            if background:
                warnings.warn("Execute in blocking mode.", Warning)
            mm = self.subscription[topic]
            start_timer = time.time()
            while True:
                if time.time() - start_timer >= timeout:
                    raise Exception("TimeoutError")
                payload_size = struct.unpack('!I', mm.buf[:4])[0]
                if payload_size:
                    payload = mmap_read(mm, payload_size)
                    break
        return payload

    def execute(self, callback=None):
        background = ZMHandler(self.publication, self.subscription,
                               self.queue, self.bq, callback)
        background.start()
        self.bg_flag = True

    def close(self, topic: Union[None, str] = None):
        if topic:
            mm = self.publication[topic]
            mm.close()
            mm.unlink()
        else:
            for mm in self.publication.values():
                mm.close()
                mm.unlink()


if __name__ == "__main__":
    sender = ZMClient()
    receiver = ZMClient()
    sender.add_publication("test")
    receiver.add_subscription("test")
    sender.publish("test", {"lol": "hahahhhhhh"}, background=False)
    # receiver.execute()
    start = time.perf_counter()
    print(receiver.receive("test", background=False))
    print((time.perf_counter() - start) * 1000, 'ms')
