import os.path
import re
from os.path import join

from setuptools import setup, find_packages


# reading package's version (same way sqlalchemy does)
with open(join(os.path.dirname(__file__), 'iso8583', '__init__.py')) as v_file:
    package_version = re.compile('.*__version__ = \'(.*?)\'', re.S) \
        .match(v_file.read()) \
        .group(1)


setup(
    name='iso8583',
    version=package_version,
    author='Mohammad sheikhian',
    description='Python library implementing the ISO-8583 banking protocol',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # This is important!
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ]
)

