from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='descent',
    version='0.1.dev0',
    description='Recursive descent parsing toolkit',
    long_description=long_description,
    url='https://github.com/ethframe/descent',
    author='ethframe',
    license='MIT',
    packages=find_packages(exclude=['examples', 'tests']),
)
