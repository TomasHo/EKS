"""__doc__"""


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'version': '0.1',
    'description': 'Datamining portálu EKS',
    'author': 'Tomas Horvath',
    'url': 'https://github.com/TomasHo/EKS.git',
    'download_url': 'https://github.com/TomasHo/EKS.git',
    'author_email': 'tomas.horvath@gmail.com',
    'install_requires': ['nose', 'bs4>=0.0.1','json','re', 'datetime', 'urllib', 'configparser', 'time'],
    'packages': ['EKS'],
    'scripts': [],
    'name': 'EKS',
    'long_description': __doc__,
    'classifiers': [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: LINUX',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
}

setup(**config)
