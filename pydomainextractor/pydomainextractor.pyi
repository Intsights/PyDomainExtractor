import typing


class DomainExtractor:
    def __init__(
        self,
        suffix_list_data: typing.Optional[str] = None,
    ) -> None: ...

    def extract(
        self,
        domain: str,
    ) -> typing.Dict[str, str]: ...

    def extract_from_url(
        self,
        url: str,
    ) -> typing.Dict[str, str]: ...

    def is_valid_domain(
        self,
        domain: str,
    ) -> bool: ...

    def get_tld_list(
        self,
    ) -> typing.List[str]: ...
