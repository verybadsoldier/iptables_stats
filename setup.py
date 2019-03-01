# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ipstatistics',

    version='0.9.0',

    description='Publish IP statistics periodically',

    author='vbs',

    author_email='vbs@springrts.de',

    keywords='mqtt iptables ipset',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    python_requires='>=3.6',

    install_requires=['ipsetpy', 'paho-mqtt', 'python-iptables', 'pyptables', 'schedule'],

    entry_points={
        'console_scripts': [
            'ipstatistics=ipban_stats.__main__:main',
        ],
    },
)