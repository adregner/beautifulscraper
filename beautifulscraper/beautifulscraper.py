# Copyright (C) 2012 by Andrew Regner <andrew@aregner.com>
#
# beautifulscraper is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import urllib2
import cookielib
from urllib import quote
from urlparse import urlparse
from bs4 import BeautifulSoup

class BeautifulScraper(object):
    """Web-scraping class that tries to handle all the things a browser handles,
    such as cookies and redirects.  It returns responses ala BeautifulSoup.
    """

    def __init__(self):
        self._headers = {}
        self._cookiejar = cookielib.CookieJar()
        self._last_request = None

        opener = urllib2.build_opener(
                BeautifulScraper.HTTPNoRedirectHandler(),
                BeautifulScraper.HTTPActualErrorProcessor(),
                urllib2.HTTPCookieProcessor(self._cookiejar),
                )
        urllib2.install_opener(opener)

    @property
    def headers(self):
        def generate_header_items():
            for header, value in self._headers.iteritems():
                if type(value) in (list, tuple):
                    for v in value:
                        yield (header, v)
                else:
                    yield (header, value)

        return [ h for h in generate_header_items() ]

    @property
    def cookies(self):
        return tuple(self._cookiejar)

    @property
    def url(self):
        return self._url

    def add_header(self, key, value):
        if key in self._headers:
            if type(self._headers[key]) == list:
                self._headers[key].append(value)
            else:
                self._headers[key] = [self._headers[key], value]
        else:
            self._headers[key] = value

    def remove_header(self, key):
        del self._headers[key]

    def set_cookie(self, key, value, domain=None, path=None):
        if self._last_request is None and (domain is None or path is None):
            raise ValueError("You must specify a domain and path for a new cookie if you haven't made a request (self.go()) yet.")

        if not domain:
            domain = ".%s" % urlparse(self._last_request.get_full_url())[1]

        if not path:
            path = urlparse(self._last_request.get_full_url())[2]

        self._cookiejar.set_cookie(cookielib.Cookie(
            0, key, value,
            None, False,
            domain, True, bool(domain[0] == '.'),
            path, True,
            secure = False,
            expires = None,
            discard = False,
            comment = None, comment_url = None,
            rest = {}
            ))

    def remove_cookie(self, key, domain=None, path=None):
        pass

    def go(self, url, data = None):
        # make the request
        self._url = url
        request = urllib2.Request(url)

        # maybe we have data
        if data:
            request.add_data(data)

        # set the headers
        for key, value in self.headers:
            request.add_header(key, value)

        # get the response
        response = urllib2.urlopen(request)

        # check for some headers that we are interested in
        self.response_headers = dict(response.headers.items())
        self.response_code = response.code

        # remember for posteraity and return the parsed response
        self._last_request = request
        return BeautifulSoup(response.read())


    class HTTPNoRedirectHandler(urllib2.HTTPRedirectHandler):
        """Sub-class of the urllib2 http redirect handler that does nothing,
        which will ensure that redirect responses are passed un-changed to the
        calling application.
        """
        def http_error_302(self, req, fp, code, msg, headers):
            return
        http_error_301 = http_error_303 = http_error_307 = http_error_302

    class HTTPActualErrorProcessor(urllib2.HTTPErrorProcessor):
        """Sub-class of the urllib2 default http error processor.  The only difference
        with this class is that 3xx return codes are not considered errors.
        """
        handler_order = urllib2.HTTPErrorProcessor.handler_order
        def http_response(self, request, response):
            if 200 <= response.code <= 399:
                return response
            else:
                return super(HTTPActualErrorProcessor, self).http_response(request, response)
        https_response = http_response

