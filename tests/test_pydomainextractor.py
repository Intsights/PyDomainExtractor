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


class DomainExtractorTldExtractTestCase(
    unittest.TestCase,
):
    domain_extractor = pydomainextractor.DomainExtractor()

    def test_american(
        self,
    ):
        url = 'http://www.google.com'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'www',
                'domain': 'google',
                'suffix': 'com',
            },
        )

    def test_british(
        self,
    ):
        url = 'http://www.theregister.co.uk'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'www',
                'domain': 'theregister',
                'suffix': 'co.uk',
            },
        )

    def test_no_subdomain(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://gmail.com',
            ),
            second={
                'subdomain': '',
                'domain': 'gmail',
                'suffix': 'com',
            },
        )

    def test_nested_subdomain(
        self,
    ):
        url = 'http://media.forums.theregister.co.uk'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'media.forums',
                'domain': 'theregister',
                'suffix': 'co.uk',
            },
        )

    def test_odd_but_possible(
        self,
    ):
        url = 'http://www.www.com'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'www',
                'domain': 'www',
                'suffix': 'com',
            },
        )
        url = 'http://www.com'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': '',
                'domain': 'www',
                'suffix': 'com',
            },
        )

    def test_suffix(
        self,
    ):
        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url(
                'com',
            )

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url(
                'co.uk',
            )

    def test_local_host(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://internalunlikelyhostname/',
            ),
            second={
                'subdomain': '',
                'domain': 'internalunlikelyhostname',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://internalunlikelyhostname.bizarre',
            ),
            second={
                'subdomain': 'internalunlikelyhostname',
                'domain': 'bizarre',
                'suffix': '',
            },
        )

    def test_qualified_local_host(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://internalunlikelyhostname.info/'
            ),
            second={
                'subdomain': '',
                'domain': 'internalunlikelyhostname',
                'suffix': 'info',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://internalunlikelyhostname.information/',
            ),
            second={
                'subdomain': 'internalunlikelyhostname',
                'domain': 'information',
                'suffix': '',
            },
        )

    def test_ip(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://216.22.0.192/',
            ),
            second={
                'subdomain': '216.22.0',
                'domain': '192',
                'suffix': '',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://216.22.project.coop/',
            ),
            second={
                'subdomain': '216.22',
                'domain': 'project',
                'suffix': 'coop',
            },
        )

    def test_looks_like_ip(
        self,
    ):
        with self.assertRaises(ValueError):
            url = u'1\xe9'
            self.domain_extractor.extract_from_url(
                url,
            )

    def test_punycode(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://xn--h1alffa9f.xn--p1ai',
            ),
            second={
                'subdomain': '',
                'domain': 'xn--h1alffa9f',
                'suffix': 'xn--p1ai',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://xN--h1alffa9f.xn--p1ai',
            ),
            second={
                'subdomain': '',
                'domain': 'xn--h1alffa9f',
                'suffix': 'xn--p1ai',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://XN--h1alffa9f.xn--p1ai',
            ),
            second={
                'subdomain': '',
                'domain': 'xn--h1alffa9f',
                'suffix': 'xn--p1ai',
            },
        )
        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url(
                'xn--tub-1m9d15sfkkhsifsbqygyujjrw602gk4li5qqk98aca0w.google.com',
            )

        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url(
                'xn--tub-1m9d15sfkkhsifsbqygyujjrw60.google.com',
            )

    def test_invalid_puny_with_puny(
        self,
    ):
        url = 'http://xn--zckzap6140b352by.blog.so-net.xn--wcvs22d.hk'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'xn--zckzap6140b352by.blog',
                'domain': 'so-net',
                'suffix': 'xn--wcvs22d.hk',
            },
        )

    def test_puny_with_non_puny_raises_value_error(
        self,
    ):
        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url(
                u'http://xn--zckzap6140b352by.blog.so-net.教育.hk',
            )

    def test_idna_2008(
        self,
    ):
        with self.assertRaises(
            ValueError,
        ):
            url = 'xn--gieen46ers-73a.de'
            self.assertEqual(
                first=self.domain_extractor.extract_from_url(
                    url,
                ),
                second={
                    'subdomain': '',
                    'domain': 'xn--gieen46ers-73a',
                    'suffix': 'de',
                },
            )

    def test_empty_raises_value_error(
        self,
    ):
        url = 'http://'
        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url(
                url,
            )

    def test_scheme(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'https://mail.google.com/mail',
            ),
            second={
                'subdomain': 'mail',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'ssh://mail.google.com/mail',
            ),
            second={
                'subdomain': 'mail',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                '//mail.google.com/mail',
            ),
            second={
                'subdomain': 'mail',
                'domain': 'google',
                'suffix': 'com',
            },
        )
    
    def test_no_protocol_raises_value_error(
        self,
    ):
        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url(
                'mail.google.com/mail',
            )

    def test_port(
        self,
    ):
        url = 'git+ssh://www.github.com:8443/'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'www',
                'domain': 'github',
                'suffix': 'com',
            },
        )

    def test_username(
        self,
    ):
        url = 'ftp://johndoe:5cr1p7k1dd13@1337.warez.com:2501'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': '1337',
                'domain': 'warez',
                'suffix': 'com',
            },
        )

    def test_query_fragment(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://google.com?q=cats',
            ),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://google.com#Welcome',
            ),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://google.com/#Welcome',
            ),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://google.com/s#Welcome',
            ),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://google.com/s?q=cats#Welcome',
            ),
            second={
                'subdomain': '',
                'domain': 'google',
                'suffix': 'com',
            },
        )

    def test_regex_order(
        self,
    ):
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://www.parliament.uk',
            ),
            second={
                'subdomain': 'www',
                'domain': 'parliament',
                'suffix': 'uk',
            },
        )
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                'http://www.parliament.co.uk',
            ),
            second={
                'subdomain': 'www',
                'domain': 'parliament',
                'suffix': 'co.uk',
            },
        )

    def test_unhandled_by_iana(
        self,
    ):
        url = 'http://www.cgs.act.edu.au/'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'www',
                'domain': 'cgs',
                'suffix': 'act.edu.au',
            },
        )
        url = 'http://www.google.com.au/'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'www',
                'domain': 'google',
                'suffix': 'com.au',
            },
        )

    def test_tld_is_a_website_too(
        self,
    ):
        url = 'http://www.metp.net.cn'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': 'www',
                'domain': 'metp',
                'suffix': 'net.cn',
            },
        )

    def test_dns_root_label_raises_value_error(
        self,
    ):
        url = 'http://www.example.com./'
        with self.assertRaises(
            ValueError,
        ):
            self.domain_extractor.extract_from_url(
                url,
            )

    def test_psl_private_domains(
        self,
    ):
        url = 'http://waiterrant.blogspot.com'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': '',
                'domain': 'waiterrant',
                'suffix': 'blogspot.com',
            },
        )

    def test_ipv4(
        self,
    ):
        url = 'http://127.0.0.1/foo/bar'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': '127.0.0',
                'domain': '1',
                'suffix': '',
            },
        )

    def test_ipv4_bad(
        self,
    ):
        url = 'http://256.256.256.256/foo/bar'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': '256.256.256',
                'domain': '256',
                'suffix': '',
            },
        )

    def test_ipv4_lookalike(
        self,
    ):
        url = 'http://127.0.0.1.9/foo/bar'
        self.assertEqual(
            first=self.domain_extractor.extract_from_url(
                url,
            ),
            second={
                'subdomain': '127.0.0.1',
                'domain': '9',
                'suffix': '',
            },
        )

    def test_extract_url(
        self,
    ):
        result = self.domain_extractor.extract_from_url(
            'http://admin:password1@www.google.com:666/secret/admin/interface?param1=42'
        )
        assert result == {
            'subdomain': 'www',
            'domain': 'google',
            'suffix': 'com',
        }
