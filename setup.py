import os
from setuptools import setup, find_packages

setup(name='django-colortools',
    version=".".join(map(str, __import__("colortools").__version__)),
    description='Colorful replacement for Django\'s testrunner',
    author='Szymon Rajchman',
    author_email='srajchman@neubloc.com',
    url='https://github.com/neubloc/django-colortools',
    packages=find_packages(),
    install_requires=['Unipath >= 0.2.1', 'Mock >= 0.7.1'],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    license="BSD",
)

