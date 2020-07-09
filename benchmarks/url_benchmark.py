import tldextract
import publicsuffix2
import tld
import pydomainextractor
import time


def benchmark_tldextract(
    urls,
):
    extractor = tldextract.TLDExtract(
        include_psl_private_domains=True,
    )

    start = time.perf_counter()

    for url in urls:
        extractor(url)

    end = time.perf_counter()

    print(f'tldextract: {end - start}s')


def benchmark_publicsuffix2(
    urls,
):
    start = time.perf_counter()

    for url in urls:
        publicsuffix2.get_sld(url)

    end = time.perf_counter()

    print(f'publicsuffix2: {end - start}s')


def benchmark_tld(
    urls,
):
    start = time.perf_counter()

    for url in urls:
        tld.parse_tld(url)

    end = time.perf_counter()

    print(f'tld: {end - start}s')


def benchmark_pydomainextractor(
    urls,
):
    extractor = pydomainextractor.DomainExtractor()

    start = time.perf_counter()

    for url in urls:
        extractor.extract_from_url(url)

    end = time.perf_counter()

    print(f'pydomainextractor: {end - start}s')


def main():
    urls = []
    with open('1m_urls') as urls_file:
        for line in urls_file:
            urls.append(line.rstrip())

    urls = urls * 10

    benchmark_tldextract(urls)
    benchmark_publicsuffix2(urls)
    benchmark_tld(urls)
    benchmark_pydomainextractor(urls)


if __name__ == '__main__':
    main()
