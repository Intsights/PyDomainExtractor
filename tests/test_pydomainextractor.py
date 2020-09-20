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

        self.assertEqual(
            first=self.domain_extractor.extract('domain.co.za'),
            second={
                'domain': 'domain',
                'subdomain': '',
                'suffix': 'co.za',
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

    def test_syntactic_invalid_domains(
        self,
    ):
        with self.assertRaises(
            expected_exception=ValueError,
        ):
            self.domain_extractor.extract('.com')

        with self.assertRaises(
            expected_exception=ValueError,
        ):
            self.domain_extractor.extract('domain..com')

        with self.assertRaises(
            expected_exception=ValueError,
        ):
            self.domain_extractor.extract('sub..domain.com')

        with self.assertRaises(
            expected_exception=ValueError,
        ):
            self.domain_extractor.extract('domain.com.')

        with self.assertRaises(
            expected_exception=ValueError,
        ):
            self.domain_extractor.extract('com.')

    def test_extract_from_url(
        self,
    ):
        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('http://www.example.com./')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('mail.google.com/mail')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('xn--gieen46ers-73a.de')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('http://')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('xn--tub-1m9d15sfkkhsifsbqygyujjrw602gk4li5qqk98aca0w.google.com')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('xn--tub-1m9d15sfkkhsifsbqygyujjrw60.google.com')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('1\xe9')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('com')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('co.uk')

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url('//mail.google.com/mail')

        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.google.com'),
            second={
                'subdomain': 'www',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.theregister.co.uk'),
            second={
                'subdomain': 'www',
                'domain': 'theregister',
                'suffix': 'co.uk',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://gmail.com'),
            second={
                'subdomain': '',
                'domain': 'gmail',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://media.forums.theregister.co.uk'),
            second={
                'subdomain': 'media.forums',
                'domain': 'theregister',
                'suffix': 'co.uk',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.www.com'),
            second={
                'subdomain': 'www',
                'domain': 'www',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.com'),
            second={
                'subdomain': '',
                'domain': 'www',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://internalunlikelyhostname/'),
            second={
                'subdomain': '',
                'domain': 'internalunlikelyhostname',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://internalunlikelyhostname.bizarre'),
            second={
                'subdomain': 'internalunlikelyhostname',
                'domain': 'bizarre',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://internalunlikelyhostname.info/'),
            second={
                'subdomain': '',
                'domain': 'internalunlikelyhostname',
                'suffix': 'info',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://internalunlikelyhostname.information/'),
            second={
                'subdomain': 'internalunlikelyhostname',
                'domain': 'information',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://216.22.0.192/'),
            second={
                'subdomain': '216.22.0',
                'domain': '192',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://216.22.project.coop/'),
            second={
                'subdomain': '216.22',
                'domain': 'project',
                'suffix': 'coop',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://xn--h1alffa9f.xn--p1ai'),
            second={
                'subdomain': '',
                'domain': 'xn--h1alffa9f',
                'suffix': 'xn--p1ai',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://xN--h1alffa9f.xn--p1ai'),
            second={
                'subdomain': '',
                'domain': 'xn--h1alffa9f',
                'suffix': 'xn--p1ai',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://XN--h1alffa9f.xn--p1ai'),
            second={
                'subdomain': '',
                'domain': 'xn--h1alffa9f',
                'suffix': 'xn--p1ai',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://xn--zckzap6140b352by.blog.so-net.xn--wcvs22d.hk'),
            second={
                'subdomain': 'xn--zckzap6140b352by.blog',
                'domain': 'so-net',
                'suffix': 'xn--wcvs22d.hk',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://xn--zckzap6140b352by.blog.so-net.教育.hk'),
            second={
                'subdomain': 'xn--zckzap6140b352by.blog',
                'domain': 'so-net',
                'suffix': '教育.hk',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('https://mail.google.com/mail'),
            second={
                'subdomain': 'mail',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('ssh://mail.google.com/mail'),
            second={
                'subdomain': 'mail',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('git+ssh://www.github.com:8443/'),
            second={
                'subdomain': 'www',
                'domain': 'github',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('ftp://johndoe:5cr1p7k1dd13@1337.warez.com:2501'),
            second={
                'subdomain': '1337',
                'domain': 'warez',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://google.com/?q=cats'),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://google.com/#Welcome'),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://google.com/#Welcome'),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://google.com/s#Welcome'),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://google.com/s?q=cats#Welcome'),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.parliament.uk'),
            second={
                'subdomain': 'www',
                'domain': 'parliament',
                'suffix': 'uk',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.parliament.co.uk'),
            second={
                'subdomain': 'www',
                'domain': 'parliament',
                'suffix': 'co.uk',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.cgs.act.edu.au/'),
            second={
                'subdomain': 'www',
                'domain': 'cgs',
                'suffix': 'act.edu.au',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.google.com.au/'),
            second={
                'subdomain': 'www',
                'domain': 'google',
                'suffix': 'com.au',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://www.metp.net.cn'),
            second={
                'subdomain': 'www',
                'domain': 'metp',
                'suffix': 'net.cn',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://waiterrant.blogspot.com'),
            second={
                'subdomain': '',
                'domain': 'waiterrant',
                'suffix': 'blogspot.com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://127.0.0.1/foo/bar'),
            second={
                'subdomain': '127.0.0',
                'domain': '1',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://256.256.256.256/foo/bar'),
            second={
                'subdomain': '256.256.256',
                'domain': '256',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://127.0.0.1.9/foo/bar'),
            second={
                'subdomain': '127.0.0.1',
                'domain': '9',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url('http://admin:password1@www.google.com:666/secret/admin/interface?param1=42'),
            second={
                'subdomain': 'www',
                'domain': 'google',
                'suffix': 'com',
            },
        )

    def test_is_valid_domain(
        self,
    ):
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('domain.com'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('sub.domain.com'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('domain.COM'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('domain.co.il'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('domain.co.za'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('domain.invalid'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('-domain.com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('domain-.com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('-sub.domain.com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('sub-.domain.com'),
        )

        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('domain.xn--mgbaakc7dvf'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('domain.اتصالات'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('xn--mgbaakc7dvf.com'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('اتصالات.com'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('اتصالات.اتصالات'),
        )
        self.assertTrue(
            expr=self.domain_extractor.is_valid_domain('xn--mgbaakc7dvf.xn--mgbaakc7dvf'),
        )

        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('domain.xn--mgbaakc7dvfa'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('domain.اsتصالات'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('xn--mgbaaskc7777dvf.com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('اتصالsات.com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('اتصالاsت.اتصالات'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('xn--mgbsaadddd1212121212kc7dvf.xn--mgbaakc7dvf'),
        )

        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('\xF0\x9F\x98\x81nonalphanum.com'),
        )

        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('.com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('domain..com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('sub..domain.com'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('domain.com.'),
        )
        self.assertFalse(
            expr=self.domain_extractor.is_valid_domain('com.'),
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

    def test_get_tld_list(
        self,
    ):
        domain_extractor = pydomainextractor.DomainExtractor(
            'com\n'
        )

        self.assertEqual(
            first=domain_extractor.get_tld_list(),
            second=[
                'com',
            ],
        )

        domain_extractor = pydomainextractor.DomainExtractor(
            'com\n'
            'net\n'
            'org\n'
            'uk.com\n'
        )

        self.assertCountEqual(
            first=domain_extractor.get_tld_list(),
            second=[
                'com',
                'net',
                'org',
                'uk.com',
            ],
        )
