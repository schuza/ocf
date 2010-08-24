#!/usr/bin/env python
'''Setup file to create an Expedient package.

Created on Aug 23, 2010

@author: jnaous
'''

from setuptools import setup, find_packages

setup(
    name="Expedient",
    version="0.2.0",
    description="Modular pluggable platform to manage GENI",
    author="Jad Naous",
    author_email="jnaous@stanford.edu",
    url="http://yuba.stanford.edu/~jnaous/expedient/",
    packages=find_packages("src/python"),
    package_dir={"": "src/python"},
    install_requires=[
        'django>=1.2.0,<1.3',
        'django_extensions',
        'django_evolution',
        'django-autoslug',
        'django-registration>=0.7,<0.8',
        'decorator',
        'M2Crypto',
        'PIL',
        'python-dateutil',
        'pycrypto',
        'paramiko',
        'django-renderform',
        'webob',
        'pyOpenSSL',
        'PyMySQL',
        'pyquery',
    ],
    extras_require={
        "docs": ["Sphinx", "pygments", "epydoc"],
    },
    include_package_data=True,
    package_data={
        "": ["/src/static", "/src/templates", "/src/wsgi"],
    },
    zip_safe=False,
)
