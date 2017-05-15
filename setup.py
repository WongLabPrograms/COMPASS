from setuptools import setup, find_packages

setup(
	name = "COMPASS",
	version = "0.1.0",
	package_dir = {"COMPASS":"code"},
	packages = ["COMPASS"],
	install_requires=["biopython","numpy"],
	author="Andrew Low",
	author_email="alow45@gmail.com",
)
