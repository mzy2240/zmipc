# zmipc
[![MIT License](https://img.shields.io/pypi/l/zmipc.svg)](https://github.com/mzy2240/zmipc/blob/master/LICENSE)
[![PyPi Version](https://img.shields.io/pypi/v/zmipc.svg)](https://pypi.python.org/pypi/zmipc/)

## Description

A Zero-copy Memory-sharing based IPC which intends to be handy in some cases where socket-based communications do not work well.

## Getting Started

The usage of zmipc intends to be straight-forward. Here is an example:

```python
from zmipc import ZMClient

sender = ZMClient()
receiver = ZMClient()
sender.add_publication(topic='test')
receiver.add_subscription(topic'test')
sender.publish(topic='test', msg='Hello World!')
print(receiver.receive(topic='test'))
```
