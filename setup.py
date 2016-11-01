"""
Installation script

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

from setuptools import setup, find_packages
import test_history_server
import os
import re

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
    version=test_history_server.__version__,
    description="Unit test history server",
    url="http://tests.karrlab.org",
    download_url='https://github.com/KarrLab/test_history_server/tarball/{}'.format(test_history_server.__version__),
    author="Jonathan Karr",
    author_email="jonrkarr@gmail.com",
    license="MIT",
    keywords='xunit junit unit test history',
    packages=find_packages(exclude=['tests', 'tests.*']),
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
