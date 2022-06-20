import os
from setuptools import find_packages, setup


def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '3.0.0'

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
  url='https://github.com/loft-orbital/graphene-federation',
  download_url=f'https://github.com/loft-orbital/graphene-federation/archive/{version}.tar.gz',
  keywords=["graphene", "graphql", "gql", "federation"],
  install_requires=[
    "graphene>=3.1",
    "graphql-core>=3.1,<3.2", # until https://github.com/graphql-python/graphene/pull/1421 is released in graphene
  ],
  classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries",
    "Programming Language :: Python :: 3.6",
  ],
  extras_require={
    "test": tests_require,
    "dev": dev_require,
  },
)
