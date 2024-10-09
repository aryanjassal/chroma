#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name="Chroma",
    version="0.4.0",
    author="Aryan Jassal",
    description="Theme any and all apps via a universal interface",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["chroma=chroma.main:main"]},
    install_requires=["lupa"],
)
