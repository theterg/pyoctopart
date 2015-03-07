from setuptools import setup
import os
import sys

if sys.version_info.major != 3:
    raise Exception("Sorry this package only works with python3.")

def read(*names):
    values = dict()
    for name in names:
        if os.path.isfile(name):
            with open(name) as f:
                value = f.read()
        else:
            value = ''
        values[name.split('.')[0]] = value
    return values

long_description = """

{README}

""".format(**read('README.md'))

setup(name='pyoctopart',
      version='0.6.1',
      description="Python library to connect to Octopart",
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved',
          'Operating System :: Unix',
      ],
      keywords='download tv show',
      author='Bernard `Guyzmo` Pratz',
      author_email='pyoctopart@m0g.net',
      url='http://m0g.net',
      license='GPLv3',
      packages=['pyoctopart'],
      zip_safe=False,
      install_requires=[
          'pyoctopart',
          'requests',
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

if "install" in sys.argv:
    print("""
Python Octopart API Library is now installed!
""")
