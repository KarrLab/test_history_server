"""
Installation script

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

from setuptools import setup, find_packages
import os
import re

# get long description
if os.path.isfile('README.rst'):
    with open('README.rst', 'r') as file:
        long_description = file.read()
else:
    long_description = ''

# get version
with open('test_history_server/VERSION', 'r') as file:
    version = file.read().strip()

# parse dependencies and their links from requirements.txt files
install_requires = []
dependency_links = []

for line in open('requirements.txt'):
    pkg_src = line.rstrip()
    match = re.match('^.+#egg=(.*?)$', pkg_src)
    if match:
        pkg_id = match.group(1)
        dependency_links.append(pkg_src)
    else:
        pkg_id = pkg_src
    install_requires.append(pkg_id)

# install package
setup(
    name="test_history_server",
    version=version,
    description="Unit test history server",
    long_description=long_description,
    url="http://tests.karrlab.org",
    download_url='https://github.com/KarrLab/test_history_server',
    author="Jonathan Karr",
    author_email="jonrkarr@gmail.com",
    license="MIT",
    keywords='xunit junit unit test history',
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={
        'test_history_server': [
            'VERSION',
        ],
    },
    install_requires=install_requires,
    dependency_links=dependency_links,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
