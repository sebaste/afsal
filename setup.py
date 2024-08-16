#!/usr/bin/env python3


from setuptools import setup, find_packages


setup(
      name="afsal",
      version="0.1.0",
      description="Set ANSI color and text attribute escape codes for text using regular expressions",
      author="Sebastian Herbertsson",
      author_email="b@454.re",
      url="https://github.com/sebaste/afsal",
      platforms="Linux",
      license="The MIT License",

      classifiers = [
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3"
          ],

      keywords = "terminal colors",

      packages = find_packages(),

      entry_points = {
          "console_scripts": ["afsal=afsal.__main__:main"],
          },
)
