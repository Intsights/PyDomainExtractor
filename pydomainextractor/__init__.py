import typing

from . import pydomainextractor


class DomainExtractor:
    '''
    PyDomainExtractor is a highly optimized Domain Name Extraction library written in Rust
    '''
    engine: typing.Optional[pydomainextractor.DomainExtractor] = None

    def __new__(
        cls,
        suffix_list_data: typing.Optional[str] = None,
    ):
        if suffix_list_data is None:
            if DomainExtractor.engine is None:
                DomainExtractor.engine = pydomainextractor.DomainExtractor()

            return DomainExtractor.engine
        else:
            return pydomainextractor.DomainExtractor(suffix_list_data)
