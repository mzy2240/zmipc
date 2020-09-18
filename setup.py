from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='zmipc',
      version='0.5',
      description='A zero-copy memory-sharing IPC on the top of mmap',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/mzy2240/zmipc',
      author='Zeyu Mao',
      author_email='mao.mzy@gmail.com',
      license='MIT',
      packages=['zmipc'],
      zip_safe=False)
