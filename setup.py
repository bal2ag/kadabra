"""
Kadabra
-------

Kadabra makes it easy to publish metrics from your Python application. It
provides a formal definition for what metrics should look like, and channels
to efficiently publish metrics from your python application to metrics storage.  
"""
import ast, re

from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('kadabra/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='Kadabra',
    version=version,
    url='http://github.com/bal2ag/kadabra/',
    license='BSD',
    author='Alex Landau',
    author_email='toozlyllc@gmail.com',
    description='A simple interface for publishing application metrics',
    long_description=__doc__,
    packages=['kadabra'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'influxdb>=3.0.0',
        'redis>=2.10',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
    
