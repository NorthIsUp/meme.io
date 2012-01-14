#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

tests_require = [
    'nose',
]

setup(
    name='memeer',
    version='0.1.0',
    author='NorthIsUp',
    author_email='opensource@disqus.com',
    url='http://github.com/NorthIsUp/memeer',
    description = 'Web server that generates adviceanimals!',
    packages=find_packages(exclude=["example_project", "tests"]),
    zip_safe=False,
    install_requires=[
        'gevent',
        'pillow',
    ],
    license='Apache License 2.0',
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    include_package_data=True,
    classifiers=[
        'Framework :: Gevent',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
