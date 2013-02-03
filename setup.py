from setuptools import setup, find_packages
from kamrecsys import __version__

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='KamRecSys',
    version=__version__,
    download_url='https://github.com/tkamishima/kamrecsys/archive/master.zip',
    license='MIT License: http://www.opensource.org/licenses/mit-license.php',
    author='Toshihiro Kamishima',
    author_email='http://www.kamishima.net/',
    url='https://github.com/tkamishima/kamrecsys',
    description='KamRecSys: Algorithms for recommender systems in Python',
    long_description=long_description,
    keywords='recommender systems',
    packages=find_packages(),
    package_data={
        'kamrecsys.datasets': ['samples/movielens*']
    },
)
