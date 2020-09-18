import mmap
import time
import pickle
import struct

mm = mmap.mmap(-1, 100, 'test')
payload = pickle.dumps("Hello")
payload_size = len(payload)
mm.seek(0)
mm.write(struct.pack('!I', payload_size))
mm.seek(4)
mm.write(payload)

while True:
    time.sleep(1)