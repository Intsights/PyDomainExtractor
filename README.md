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
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)


## About The Project

PyDomainExtractor is a library intended for parsing domain names into their parts fast. The library is written in C++ to achieve the highest performance possible.


### Built With

* [GNU libidn2](https://www.gnu.org/software/libidn/#libidn2)
* [Public Suffix List](https://publicsuffix.org/)


### Performance

Test was measured on a file containing 10 million random domains from various TLDs

| Library  | Function | Time | Improvement Factor |
| ------------- | ------------- | ------------- | ------------- |
| [tldextract](https://github.com/john-kurkowski/tldextract) | \_\_call\_\_ | 67.0s | 1.0x |
| [publicsuffix2](https://github.com/nexb/python-publicsuffix2) | publicsuffix2.get_tld | 25.8s | 2.6x |
| [PyDomainExtractor](https://github.com/Intsights/PyDomainExtractor) | pydomainextractor.extract | 2.76s | 24.3x |

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

The usual use case:
```python
import pydomainextractor


# Loads the current supplied version of PublicSuffixList from the repository. Does not download any data.
pydomainextractor.load()

pydomainextractor.extract('google.com')
>>> {
>>>     'subdomain': '',
>>>     'domain': 'google',
>>>     'suffix': 'com'
>>> }

# Loads a custom SuffixList data. Should follow PublicSuffixList's format.
pydomainextractor.load(
    'tld\n'
    'custom.tld\n'
)

pydomainextractor.extract('google.com')
>>> {
>>>     'subdomain': 'google',
>>>     'domain': 'com',
>>>     'suffix': ''
>>> }

pydomainextractor.extract('google.custom.tld')
>>> {
>>>     'subdomain': '',
>>>     'domain': 'google',
>>>     'suffix': 'custom.tld'
>>> }
```



## License

Distributed under the MIT License. See `LICENSE` for more information.


## Contact

Gal Ben David - gal@intsights.com

Project Link: [https://github.com/Intsights/PyDomainExtractor](https://github.com/Intsights/PyDomainExtractor)




[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=flat-square
