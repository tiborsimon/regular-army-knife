from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='regular-army-knife',
      version='0.0.0',
      description='The advanced regular expression studio.',
      long_description=readme(),
      test_suite='test',
      classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Topic :: Utilities',
            'Environment :: Console',
            'Natural Language :: English',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: Unix',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7',
            'Topic :: Text Processing :: Linguistic',
      ],
      url='https://github.com/tiborsimon/regular-army-knife',
      keywords='regex regular expression studio',
      author='Tibor Simon',
      author_email='tibor@tiborsimon.io',
      license='MIT',
      packages=['rak'],
      scripts=['bin/r'],
      include_package_data=True,
      zip_safe=False)
