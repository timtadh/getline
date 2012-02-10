from distutils.core import setup
import getline

setup(name='getline',
      version=str('master'),
      description=('A library to get text from the console.'),
      author='Tim Henderson',
      author_email='tim.tadh@gmail.com',
      url='https://www.github.com/timtadh/getline',
      license='BSD',
      provides=['getline'],
      packages=['getline'],
      platforms=['unix', 'darwin', 'windows'],
      data_files=[('.', ['LICENSE', 'README'])],
)

