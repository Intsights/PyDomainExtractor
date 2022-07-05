<p align="center">
    <a href="https://github.com/Intsights/PyDomainExtractor">
        <img src="https://raw.githubusercontent.com/Intsights/PyDomainExtractor/master/images/logo.png" alt="Logo">
    </a>
    <h3 align="center">
        A blazingly fast domain extraction library written in Rust
    </h3>
</p>

![license](https://img.shields.io/badge/MIT-License-blue)
![Python](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)
![Build](https://github.com/Intsights/PyDomainExtractor/workflows/Build/badge.svg)
[![PyPi](https://img.shields.io/pypi/v/PyDomainExtractor.svg)](https://pypi.org/project/PyDomainExtractor/)

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About The Project](#about-the-project)
  - [Built With](#built-with)
  - [Performance](#performance)
    - [Extract From Domain](#extract-from-domain)
    - [Extract From URL](#extract-from-url)
  - [Installation](#installation)
- [Usage](#usage)
  - [Extraction](#extraction)
  - [URL Extraction](#url-extraction)
  - [Validation](#validation)
  - [TLDs List](#tlds-list)
- [License](#license)
- [Contact](#contact)


## About The Project

PyDomainExtractor is a Python library designed to parse domain names quickly.
In order to achieve the highest performance possible, the library was written in Rust.


### Built With

* [AHash](https://github.com/tkaitchuck/aHash)
* [idna](https://github.com/servo/rust-url/)
* [memchr](https://github.com/BurntSushi/memchr)
* [once_cell](https://github.com/matklad/once_cell)
* [Public Suffix List](https://publicsuffix.org/)


### Performance


#### Extract From Domain

Tests were run on a file containing 10 million random domains from various top-level domains (Mar. 13rd 2022)

| Library  | Function | Time |
| ------------- | ------------- | ------------- |
| [PyDomainExtractor](https://github.com/Intsights/PyDomainExtractor) | pydomainextractor.extract | 1.50s |
| [publicsuffix2](https://github.com/nexb/python-publicsuffix2) | publicsuffix2.get_sld | 9.92s |
| [tldextract](https://github.com/john-kurkowski/tldextract) | \_\_call\_\_ | 29.23s |
| [tld](https://github.com/barseghyanartur/tld) | tld.parse_tld | 34.48s |


#### Extract From URL

The test was conducted on a file containing 1 million random urls (Mar. 13rd 2022)

| Library  | Function | Time |
| ------------- | ------------- | ------------- |
| [PyDomainExtractor](https://github.com/Intsights/PyDomainExtractor) | pydomainextractor.extract_from_url | 2.24s |
| [publicsuffix2](https://github.com/nexb/python-publicsuffix2) | publicsuffix2.get_sld | 10.84s |
| [tldextract](https://github.com/john-kurkowski/tldextract) | \_\_call\_\_ | 36.04s |
| [tld](https://github.com/barseghyanartur/tld) | tld.parse_tld | 57.87s |


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

domain_extractor.extract_from_url('http://google.com/')
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


### TLDs List

```python
import pydomainextractor


# Loads the current supplied version of PublicSuffixList from the repository. Does not download any data.
domain_extractor = pydomainextractor.DomainExtractor()

domain_extractor.get_tld_list()
>>> [
>>>     'bostik',
>>>     'backyards.banzaicloud.io',
>>>     'biz.bb',
>>>     ...
>>> ]
```


## License

Distributed under the MIT License. See `LICENSE` for more information.


## Contact

Gal Ben David - gal@intsights.com

Project Link: [https://github.com/Intsights/PyDomainExtractor](https://github.com/Intsights/PyDomainExtractor)




[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=flat-square
