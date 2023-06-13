import os
from setuptools import find_packages, setup


def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '3.1.4'

tests_require = [
    "pytest==7.1.2",
    "pytest-cov",
]

dev_require = [
    "black==22.3.0",
    "flake8==4.0.1",
    "mypy==0.961",
] + tests_require

setup(
  name='graphene-federation',
  packages=find_packages(exclude=["tests"]),
  version=version,
  license='MIT',
  description = 'Federation implementation for graphene',
  long_description=(read('README.md')),
  long_description_content_type='text/markdown',
  author='Igor Kasianov',
  author_email='super.hang.glider@gmail.com',
  url='https://github.com/graphql-python/graphene-federation',
  download_url=f'https://github.com/graphql-python/graphene-federation/archive/{version}.tar.gz',
  keywords=["graphene", "graphql", "gql", "federation"],
  install_requires=[
    "graphene>=3.1",
    "graphql-core>=3.1",
  ],
  classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
  ],
  extras_require={
    "test": tests_require,
    "dev": dev_require,
  },
)
