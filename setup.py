import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name = 'pybeamer',
  version = '1.0.0',
  license='GPL-3.0',
  description = '',
  long_description = long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  author = 'João Victor da Fonseca Pinto, Werner Freund',
  author_email = 'jodafons@lps.ufrj.br',
  url = 'https://github.com/jodafons/maestro',
  keywords = [],
  install_requires=[
          'numpy',
          'six',
          'scipy',
          'future'
      ],
)