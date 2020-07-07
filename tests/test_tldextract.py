# -*- coding: utf-8 -*-
import unittest
import tldextract
import pydomainextractor


# extract = tldextract.TLDExtract(cache_file=False)
extract = pydomainextractor.DomainExtractor()


def assert_extract(  # pylint: disable=missing-docstring
    url,
    expected_domain_data,
    expected_ip_data='',
    extractor=extract,
):
    expected_fqdn, expected_subdomain, expected_domain, expected_tld = expected_domain_data
    result = extractor.extract_from_url(url)
    assert expected_subdomain == result['subdomain']
    assert expected_domain == result['domain']
    assert expected_tld == result['suffix']
    # assert expected_ip_data == ext.get('ipv4')
    # assert expected_fqdn == ext.get('fqdn')


class DomainExtractorTldExtractTestCase(
    unittest.TestCase
):
    def test_american(
        self,
    ):
        assert_extract('http://www.google.com',
                    ('www.google.com', 'www', 'google', 'com'))

    def test_british(
        self,
    ):
        assert_extract("http://www.theregister.co.uk",
                    ("www.theregister.co.uk", "www", "theregister", "co.uk"))


    def test_no_subdomain(
        self,
    ):
        assert_extract("http://gmail.com", ("gmail.com", "", "gmail", "com"))


    def test_nested_subdomain(
        self,
    ):
        assert_extract("http://media.forums.theregister.co.uk",
                    ("media.forums.theregister.co.uk", "media.forums",
                        "theregister", "co.uk"))


    def test_odd_but_possible(
        self,
    ):
        assert_extract('http://www.www.com', ('www.www.com', 'www', 'www', 'com'))
        assert_extract('http://www.com', ('www.com', '', 'www', 'com'))

    def test_suffix(
        self,
    ):
        with self.assertRaises(
            ValueError,
        ):
            assert_extract('com', ('', '', '', 'com'))
            assert_extract('co.uk', ('', '', '', 'co.uk'))

    def test_local_host(
        self,
    ):
        assert_extract('http://internalunlikelyhostname/',
                    ('', '', 'internalunlikelyhostname', ''))
        assert_extract('http://internalunlikelyhostname.bizarre',
                    ('', 'internalunlikelyhostname', 'bizarre', ''))


    def test_qualified_local_host(
        self,
    ):
        assert_extract('http://internalunlikelyhostname.info/',
                    ('internalunlikelyhostname.info',
                        '', 'internalunlikelyhostname', 'info'))
        assert_extract('http://internalunlikelyhostname.information/',
                    ('',
                        'internalunlikelyhostname', 'information', ''))


    def test_ip(
        self,
    ):
        assert_extract('http://216.22.0.192/',
                    ('', '', '216.22.0.192', ''),
                    expected_ip_data='216.22.0.192',)
        assert_extract('http://216.22.project.coop/',
                    ('216.22.project.coop', '216.22', 'project', 'coop'))


    def test_looks_like_ip(
        self,
    ):
        with self.assertRaises(ValueError):
            assert_extract(u'1\xe9', ('', '', u'1\xe9', ''))



    def test_punycode(
        self,
    ):
        assert_extract('http://xn--h1alffa9f.xn--p1ai',
                    ('xn--h1alffa9f.xn--p1ai', '', 'xn--h1alffa9f', 'xn--p1ai'))
        assert_extract('http://xN--h1alffa9f.xn--p1ai',
                    ('xN--h1alffa9f.xn--p1ai', '', 'xN--h1alffa9f', 'xn--p1ai'))
        assert_extract('http://XN--h1alffa9f.xn--p1ai',
                    ('XN--h1alffa9f.xn--p1ai', '', 'XN--h1alffa9f', 'xn--p1ai'))
        # Entries that might generate UnicodeError exception
        # This subdomain generates UnicodeError 'IDNA does not round-trip'
        assert_extract('xn--tub-1m9d15sfkkhsifsbqygyujjrw602gk4li5qqk98aca0w.google.com',
                    ('xn--tub-1m9d15sfkkhsifsbqygyujjrw602gk4li5qqk98aca0w.google.com',
                        'xn--tub-1m9d15sfkkhsifsbqygyujjrw602gk4li5qqk98aca0w', 'google',
                        'com'))
        # This subdomain generates UnicodeError 'incomplete punicode string'
        assert_extract('xn--tub-1m9d15sfkkhsifsbqygyujjrw60.google.com',
                    ('xn--tub-1m9d15sfkkhsifsbqygyujjrw60.google.com',
                        'xn--tub-1m9d15sfkkhsifsbqygyujjrw60', 'google', 'com'))


    def test_invalid_puny_with_puny(
        self,
    ):
        assert_extract('http://xn--zckzap6140b352by.blog.so-net.xn--wcvs22d.hk',
                    ('xn--zckzap6140b352by.blog.so-net.xn--wcvs22d.hk',
                        'xn--zckzap6140b352by.blog', 'so-net', 'xn--wcvs22d.hk'))


    def test_puny_with_non_puny(
        self,
    ):
        assert_extract(u'http://xn--zckzap6140b352by.blog.so-net.教育.hk',
                    (u'xn--zckzap6140b352by.blog.so-net.教育.hk',
                        'xn--zckzap6140b352by.blog', 'so-net', u'教育.hk'))


    def test_idna_2008(
        self,
    ):
        """Python supports IDNA 2003.
        The IDNA library adds 2008 support for characters like ß.
        """
        with self.assertRaises(
            ValueError,
        ):
            assert_extract('xn--gieen46ers-73a.de',
                        ('xn--gieen46ers-73a.de', '', 'xn--gieen46ers-73a', 'de'))


    def test_empty(
        self,
    ):
        assert_extract('http://', ('', '', '', ''))


    def test_scheme(
        self,
    ):
        assert_extract('https://mail.google.com/mail', ('mail.google.com', 'mail', 'google', 'com'))
        assert_extract('ssh://mail.google.com/mail', ('mail.google.com', 'mail', 'google', 'com'))
        assert_extract('//mail.google.com/mail', ('mail.google.com', 'mail', 'google', 'com'))
        assert_extract('mail.google.com/mail',
                    ('mail.google.com', 'mail', 'google', 'com'), extractor=extract)


    def test_port(
        self,
    ):
        assert_extract('git+ssh://www.github.com:8443/', ('www.github.com', 'www', 'github', 'com'))


    def test_username(
        self,
    ):
        assert_extract('ftp://johndoe:5cr1p7k1dd13@1337.warez.com:2501',
                    ('1337.warez.com', '1337', 'warez', 'com'))


    def test_query_fragment(
        self,
    ):
        assert_extract('http://google.com?q=cats', ('google.com', '', 'google', 'com'))
        assert_extract('http://google.com#Welcome', ('google.com', '', 'google', 'com'))
        assert_extract('http://google.com/#Welcome', ('google.com', '', 'google', 'com'))
        assert_extract('http://google.com/s#Welcome', ('google.com', '', 'google', 'com'))
        assert_extract('http://google.com/s?q=cats#Welcome', ('google.com', '', 'google', 'com'))


    def test_regex_order(
        self,
    ):
        assert_extract('http://www.parliament.uk',
                    ('www.parliament.uk', 'www', 'parliament', 'uk'))
        assert_extract('http://www.parliament.co.uk',
                    ('www.parliament.co.uk', 'www', 'parliament', 'co.uk'))


    def test_unhandled_by_iana(
        self,
    ):
        assert_extract('http://www.cgs.act.edu.au/',
                    ('www.cgs.act.edu.au', 'www', 'cgs', 'act.edu.au'))
        assert_extract('http://www.google.com.au/',
                    ('www.google.com.au', 'www', 'google', 'com.au'))


    def test_tld_is_a_website_too(
        self,
    ):
        assert_extract('http://www.metp.net.cn', ('www.metp.net.cn', 'www', 'metp', 'net.cn'))
        # This is unhandled by the PSL. Or is it?
        # assert_extract(http://www.net.cn',
        #                ('www.net.cn', 'www', 'net', 'cn'))


    def test_dns_root_label(
        self,
    ):
        assert_extract('http://www.example.com./',
                    ('www.example.com', 'www', 'example', 'com'))


    def test_private_domains(
        self,
    ):
        assert_extract('http://waiterrant.blogspot.com',
                    ('waiterrant.blogspot.com', 'waiterrant', 'blogspot', 'com'))


    def test_ipv4(
        self,
    ):
        assert_extract('http://127.0.0.1/foo/bar',
                    ('', '', '127.0.0.1', ''),
                    expected_ip_data='127.0.0.1')


    def test_ipv4_bad(
        self,
    ):
        assert_extract('http://256.256.256.256/foo/bar',
                    ('', '256.256.256', '256', ''),
                    expected_ip_data='')


    def test_ipv4_lookalike(
        self,
    ):
        assert_extract('http://127.0.0.1.9/foo/bar',
                    ('', '127.0.0.1', '9', ''),
                    expected_ip_data='')


    def test_result_as_dict(
        self,
    ):
        result = extract.extract(
            "http://admin:password1@www.google.com:666"
            "/secret/admin/interface?param1=42"
        )
        expected_dict = {'subdomain': 'www',
                        'domain': 'google',
                        'suffix': 'com'}
        assert result == expected_dict


    # @responses.activate  # pylint: disable=no-member
    # def test_cache_timeouts(
    #     self,
    # ):
    #     server = 'http://some-server.com'
    #     responses.add(  # pylint: disable=no-member
    #         responses.GET,  # pylint: disable=no-member
    #         server,
    #         status=408
    #     )

    #     assert tldextract.remote.find_first_response([server], 5) == ''


    def test_extract_url(
        self,
    ):
        result = extract.extract_from_url(
            "http://admin:password1@www.google.com:666"
            "/secret/admin/interface?param1=42"
        )
        assert result == 'www.google.com'
