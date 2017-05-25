#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name = "COMPASS",
	version = "0.1.0",
	packages = ["compass"],
	scripts = ["bin/COMPASS.py","bin/wrap_COMPASS.py"],
	install_requires=["biopython","numpy"],
	author="Andrew Low",
	author_email="alow45@gmail.com",
)
