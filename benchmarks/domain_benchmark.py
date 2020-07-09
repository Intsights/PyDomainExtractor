import tldextract
import publicsuffix2
import tld
import pydomainextractor
import time


def benchmark_tldextract(
    domains,
):
    extractor = tldextract.TLDExtract(
        include_psl_private_domains=True,
    )

    start = time.perf_counter()

    for domain in domains:
        extractor(domain)

    end = time.perf_counter()

    print(f'tldextract: {end - start}s')


def benchmark_publicsuffix2(
    domains,
):
    start = time.perf_counter()

    for domain in domains:
        publicsuffix2.get_sld(domain)

    end = time.perf_counter()

    print(f'publicsuffix2: {end - start}s')


def benchmark_tld(
    domains,
):
    start = time.perf_counter()

    for domain in domains:
        tld.parse_tld(domain)

    end = time.perf_counter()

    print(f'tld: {end - start}s')


def benchmark_pydomainextractor(
    domains,
):
    extractor = pydomainextractor.DomainExtractor()

    start = time.perf_counter()

    for domain in domains:
        extractor.extract(domain)

    end = time.perf_counter()

    print(f'pydomainextractor: {end - start}s')


def main():
    domains = []
    with open('10m_domains') as domains_file:
        for line in domains_file:
            domains.append(line.rstrip())

    benchmark_tldextract(domains)
    benchmark_publicsuffix2(domains)
    benchmark_tld(domains)
    benchmark_pydomainextractor(domains)


if __name__ == '__main__':
    main()
