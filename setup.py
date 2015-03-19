from setuptools import setup, find_packages

setup(name='ndayslater',
      version='1.0',
      description='Schedule mails for resubmission N days later',
      author='Thomas Guettler',
      author_email='info.ndayslater@thomas-guettler.de',
      url='https://github.com/guettli/ndayslater',
      packages=find_packages(),
      install_requires=['configargparse', 'imapclient'],
      entry_points={
          'console_scripts': [
              'ndayslater = ndayslater.ndayslater:main',
              ]
      }
     )
