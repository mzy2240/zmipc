from setuptools import setup

setup(name='zmipc',
      version='0.1',
      description='A zero-copy memory-sharing IPC on the top of mmap',
      url='http://github.com/mzy2240/zmipc',
      author='Zeyu Mao',
      author_email='mao.mzy@gmail.com',
      license='MIT',
      packages=['zmipc'],
      zip_safe=False)
