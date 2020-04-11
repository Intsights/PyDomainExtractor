import unittest
import unittest.mock

import pydomainextractor


class DomainExtractorExtractionTestCase(
    unittest.TestCase,
):
    def setUp(
        self,
    ):
        self.domain_extractor = pydomainextractor.DomainExtractor()

    def test_extract_only_tld(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract('com'),
            second={
                'domain': '',
                'subdomain': '',
                'suffix': 'com',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('jp.net'),
            second={
                'domain': '',
                'subdomain': '',
                'suffix': 'jp.net',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('鹿児島.jp'),
            second={
                'domain': '',
                'subdomain': '',
                'suffix': '鹿児島.jp',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('香格里拉'),
            second={
                'domain': '',
                'subdomain': '',
                'suffix': '香格里拉',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('xn--32vp30h.jp'),
            second={
                'domain': '',
                'subdomain': '',
                'suffix': 'xn--32vp30h.jp',
            },
        )

    def test_extract_only_domain(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract('nonexistenttld'),
            second={
                'domain': 'nonexistenttld',
                'subdomain': '',
                'suffix': '',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('香格里拉香格里拉香格里拉'),
            second={
                'domain': '香格里拉香格里拉香格里拉',
                'subdomain': '',
                'suffix': '',
            },
        )

    def test_extract_only_domain_and_subdomain(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract('nonexistenttld.nonexistenttld'),
            second={
                'domain': 'nonexistenttld',
                'subdomain': 'nonexistenttld',
                'suffix': '',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('香格里拉香格里拉香格里拉.nonexistenttld'),
            second={
                'domain': 'nonexistenttld',
                'subdomain': '香格里拉香格里拉香格里拉',
                'suffix': '',
            },
        )

    def test_extract_all_parts(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract('google.com'),
            second={
                'domain': 'google',
                'subdomain': '',
                'suffix': 'com',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('subdomain.google.com'),
            second={
                'domain': 'google',
                'subdomain': 'subdomain',
                'suffix': 'com',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('subsubdomain.subdomain.google.com'),
            second={
                'domain': 'google',
                'subdomain': 'subsubdomain.subdomain',
                'suffix': 'com',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('subsubdomain.subdomain.google.香格里拉'),
            second={
                'domain': 'google',
                'subdomain': 'subsubdomain.subdomain',
                'suffix': '香格里拉',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('subsubdomain.subdomain.google.鹿児島.jp'),
            second={
                'domain': 'google',
                'subdomain': 'subsubdomain.subdomain',
                'suffix': '鹿児島.jp',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('subsubdomain.subdomain.google.xn--32vp30h.jp'),
            second={
                'domain': 'google',
                'subdomain': 'subsubdomain.subdomain',
                'suffix': 'xn--32vp30h.jp',
            },
        )

    def test_special_cases(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract('bla.ck'),
            second={
                'domain': '',
                'subdomain': '',
                'suffix': 'bla.ck',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('a.bla.ck'),
            second={
                'domain': 'a',
                'subdomain': '',
                'suffix': 'bla.ck',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('a.b.bla.ck'),
            second={
                'domain': 'b',
                'subdomain': 'a',
                'suffix': 'bla.ck',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('www.ck'),
            second={
                'domain': 'www',
                'subdomain': '',
                'suffix': 'ck',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('a.www.ck'),
            second={
                'domain': 'www',
                'subdomain': 'a',
                'suffix': 'ck',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('a.bzz.dapps.earth'),
            second={
                'domain': '',
                'subdomain': '',
                'suffix': 'a.bzz.dapps.earth',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('a.b.bzz.dapps.earth'),
            second={
                'domain': 'a',
                'subdomain': '',
                'suffix': 'b.bzz.dapps.earth',
            },
        )

    def test_upper_case(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract('domain.Com'),
            second={
                'domain': 'domain',
                'subdomain': '',
                'suffix': 'com',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('DOmain.Com'),
            second={
                'domain': 'domain',
                'subdomain': '',
                'suffix': 'com',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('DOmain.COM'),
            second={
                'domain': 'domain',
                'subdomain': '',
                'suffix': 'com',
            },
        )

        self.assertEqual(
            first=self.domain_extractor.extract('a.b.bla.CK'),
            second={
                'domain': 'b',
                'subdomain': 'a',
                'suffix': 'bla.ck',
            },
        )


class DomainExtractorLoadTestCase(
    unittest.TestCase,
):
    def test_load_called_without_data(
        self,
    ):
        domain_extractor = pydomainextractor.DomainExtractor()

        self.assertEqual(
            first=domain_extractor.extract('com'),
            second={
                'subdomain': '',
                'domain': '',
                'suffix': 'com',
            },
        )

    def test_load_called_with_data(
        self,
    ):
        domain_extractor = pydomainextractor.DomainExtractor(
            'com\n'
        )

        self.assertEqual(
            first=domain_extractor.extract('com'),
            second={
                'subdomain': '',
                'domain': '',
                'suffix': 'com',
            },
        )

        domain_extractor = pydomainextractor.DomainExtractor(
            'net\n'
        )

        self.assertEqual(
            first=domain_extractor.extract('com'),
            second={
                'subdomain': '',
                'domain': 'com',
                'suffix': '',
            },
        )

        domain_extractor = pydomainextractor.DomainExtractor(
            'customtld\n'
        )

        self.assertEqual(
            first=domain_extractor.extract('google.customtld'),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'customtld',
            },
        )

        domain_extractor = pydomainextractor.DomainExtractor(
            'tld\n'
            'custom.tld\n'
        )

        self.assertEqual(
            first=domain_extractor.extract('google.custom.tld'),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'custom.tld',
            },
        )
