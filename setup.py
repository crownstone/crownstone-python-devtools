#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='crownstone-devtools',
    version="0.4.0",
    packages=find_packages(exclude=["examples","testing"]),
    author="Crownstone B.V.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crownstone/crownstone-python-devtools",
    install_requires=list(package.strip() for package in open('requirements.txt')),
    scripts=[
        'crownstone_devtools/cs_microapp_create_header',
        'crownstone_devtools/cs_bluenet_log_client',
        'crownstone_devtools/cs_bluenet_extract_log_strings',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ],
    python_requires='>=3.7',
)
