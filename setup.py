from setuptools import setup
import os
import sys

setup(name='pyoctopart',
      version='0.6.3',
      description="Python library to connect to Octopart",
      long_description_markdown_filename='README.md',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved',
          'Operating System :: Unix',
      ],
      keywords='download tv show',
      author='Bernard `Guyzmo` Pratz',
      author_email='pyoctopart@m0g.net',
      url='https://github.com/guyzmo/pyoctopart',
      license='GPLv3',
      packages=['pyoctopart'],
      zip_safe=False,
      setup_requires=['setuptools-markdown'],
      install_requires=[
          'pyoctopart',
          'requests',
          'setuptools',
      ],
      )

if "install" in sys.argv:
    print("""
Python Octopart API Library is now installed!

To start using it, call:

    python3
    >>> from pyoctopart.octopart import Octopart
    >>> help(Octopart)

""")
