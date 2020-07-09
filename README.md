<p align="center">
    <a href="https://github.com/Intsights/PyDomainExtractor">
        <img src="https://raw.githubusercontent.com/Intsights/PyDomainExtractor/master/images/logo.png" alt="Logo">
    </a>
    <h3 align="center">
        Highly optimized domain name extraction library written in C++
    </h3>
</p>

![license](https://img.shields.io/badge/MIT-License-blue)
![Python](https://img.shields.io/badge/Python-3.6%20%7C%203.7%20%7C%203.8-blue)
![Build](https://github.com/Intsights/PyDomainExtractor/workflows/Build/badge.svg)
[![PyPi](https://img.shields.io/pypi/v/PyDomainExtractor.svg)](https://pypi.org/project/PyDomainExtractor/)

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About The Project](#about-the-project)
  - [Built With](#built-with)
  - [Performance](#performance)
    - [Extract From Domain](#extract-from-domain)
    - [Extract From URL](#extract-from-url)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Extraction](#extraction)
  - [URL Extraction](#url-extraction)
  - [Validation](#validation)
- [License](#license)
- [Contact](#contact)


## About The Project

PyDomainExtractor is a library intended for parsing domain names into their parts fast. The library is written in C++ to achieve the highest performance possible.


### Built With

* [GNU libidn2](https://www.gnu.org/software/libidn/#libidn2)
* [Tessil/robin-map](https://github.com/Tessil/robin-map)
* [Public Suffix List](https://publicsuffix.org/)


### Performance


#### Extract From Domain

Test was measured on a file containing 10 million random domains from various TLDs

| Library  | Function | Time |
| ------------- | ------------- | ------------- |
| [PyDomainExtractor](https://github.com/Intsights/PyDomainExtractor) | pydomainextractor.extract | 2.21s |
| [publicsuffix2](https://github.com/nexb/python-publicsuffix2) | publicsuffix2.get_sld | 16.53s |
| [tldextract](https://github.com/john-kurkowski/tldextract) | \_\_call\_\_ | 42.45s |
| [tld](https://github.com/barseghyanartur/tld) | publicsuffix2.get_tld | 47.07s |


#### Extract From URL

Test was measured on a file containing 1 million random urls

| Library  | Function | Time |
| ------------- | ------------- | ------------- |
| [PyDomainExtractor](https://github.com/Intsights/PyDomainExtractor) | pydomainextractor.extract | 0.28s |
| [publicsuffix2](https://github.com/nexb/python-publicsuffix2) | publicsuffix2.get_sld | 1.91s |
| [tldextract](https://github.com/john-kurkowski/tldextract) | \_\_call\_\_ | 5.55s |
| [tld](https://github.com/barseghyanartur/tld) | publicsuffix2.get_tld | 5.98s |


### Prerequisites

In order to compile this package you should have GCC, libidn2, and Python development package installed.
* Fedora
```sh
sudo dnf install python3-devel libidn2-devel gcc-c++
```
* Ubuntu 18.04
```sh
sudo apt install python3-dev libidn2-dev g++-9
```


### Installation

```sh
pip3 install PyDomainExtractor
```


## Usage


### Extraction

```python
import pydomainextractor


# Loads the current supplied version of PublicSuffixList from the repository. Does not download any data.
domain_extractor = pydomainextractor.DomainExtractor()

domain_extractor.extract('google.com')
>>> {
>>>     'subdomain': '',
>>>     'domain': 'google',
>>>     'suffix': 'com'
>>> }

# Loads a custom SuffixList data. Should follow PublicSuffixList's format.
domain_extractor = pydomainextractor.DomainExtractor(
    'tld\n'
    'custom.tld\n'
)

domain_extractor.extract('google.com')
>>> {
>>>     'subdomain': 'google',
>>>     'domain': 'com',
>>>     'suffix': ''
>>> }

domain_extractor.extract('google.custom.tld')
>>> {
>>>     'subdomain': '',
>>>     'domain': 'google',
>>>     'suffix': 'custom.tld'
>>> }
```


### URL Extraction

```python
import pydomainextractor


# Loads the current supplied version of PublicSuffixList from the repository. Does not download any data.
domain_extractor = pydomainextractor.DomainExtractor()

domain_extractor.extract('http://google.com/')
>>> {
>>>     'subdomain': '',
>>>     'domain': 'google',
>>>     'suffix': 'com'
>>> }
```


### Validation

```python
import pydomainextractor


# Loads the current supplied version of PublicSuffixList from the repository. Does not download any data.
domain_extractor = pydomainextractor.DomainExtractor()

domain_extractor.is_valid_domain('google.com')
>>> True

domain_extractor.is_valid_domain('domain.اتصالات')
>>> True

domain_extractor.is_valid_domain('xn--mgbaakc7dvf.xn--mgbaakc7dvf')
>>> True

domain_extractor.is_valid_domain('domain-.com')
>>> False

domain_extractor.is_valid_domain('-sub.domain.com')
>>> False

domain_extractor.is_valid_domain('\xF0\x9F\x98\x81nonalphanum.com')
>>> False
```


## License

Distributed under the MIT License. See `LICENSE` for more information.


## Contact

Gal Ben David - gal@intsights.com

Project Link: [https://github.com/Intsights/PyDomainExtractor](https://github.com/Intsights/PyDomainExtractor)




[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=flat-square
