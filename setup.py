from setuptools import setup

import os
import pathlib
import sys

package_name = pathlib.Path(__file__).resolve().parent.name

sys.path.insert(0, os.path.join(os.path.dirname(__file__), package_name))
from __version__ import __version__

setup(
    name=package_name,
    author='csm10495',
    author_email='csm10495@gmail.com',
    url='http://github.com/csm10495/' + package_name,
    version=__version__,
    packages=[package_name],
    license='MIT License',
    python_requires='>=3.7',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    include_package_data = True,
    install_requires=['requests', 'cachetools'],
    entry_points={},
)