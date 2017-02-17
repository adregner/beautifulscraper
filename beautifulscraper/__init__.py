# Copyright (C) 2012 by Andrew Regner <andrew@aregner.com>
#
# beautifulscraper is freely distributable under the terms
# of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.
import sys
if sys.version_info[0] < 3:
    import urllib2
    import cookielib
    from urllib import quote
    from urlparse import urlparse
else:
    import urllib.request as urllib2
    import http.cookiejar as cookielib
    from urllib.request import quote
    from urllib.parse import urlparse
from bs4 import BeautifulSoup


class BeautifulScraper(object):
    """Web-scraping class that tries to handle all the things a browser handles,
    such as cookies and redirects.  It returns responses ala BeautifulSoup.
    """

    def __init__(self):
        """This creates a new BeautifulScraper instance.  The only thing to note
        about what this does is that the underlying CookieJar instance is stored
        only in memory, and is an instance attribute of your current
        BeautifulScraper instance.
        """
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
        """Returns a list of tuples in (header_name, header_value) form.
        This is done to allow a single header (such as Location or Accept)
        to have multiple values, weather or not that makes sense.
        """
        def generate_header_items():
            for header, value in self._headers.items():
                if type(value) in (list, tuple):
                    for v in value:
                        yield (header, v)
                else:
                    yield (header, value)

        return [h for h in generate_header_items()]

    @property
    def cookies(self):
        """Returns a tuple of all the Cookie instances in the CookieJar.
        """
        return tuple(self._cookiejar)

    @property
    def url(self):
        """Returns the current url
        """
        return self._url

    def add_header(self, key, value):
        """Adds a header to the list of headers submitted with every request.  It is
        possiable to have a single header_key have multiple values.  In that case,
        the header will be specified multiple times in the underlying HTTP request.
        """
        if key in self._headers:
            if type(self._headers[key]) == list:
                self._headers[key].append(value)
            else:
                self._headers[key] = [self._headers[key], value]
        else:
            self._headers[key] = value

    def remove_header(self, key):
        """Removes a header_key from the headers submitted with every request.  If
        there are multiple values assigned to this header_key, they will all be removed.
        """
        del self._headers[key]

    def set_cookie(self, key, value, domain=None, path=None):
        """Saves a Cookie instance into the underlying CookieJar instance.  It will be
        submitted (as approperate, based on the request's domain, path, security, etc...)
        along with any further requests.  You can specify the domain and path the cookie
        should be valid for.  These need to be specified if there have been no requests
        made yet with the current BeautifulScraper instance.  Otherwise, they are
        optional.  The cookies set this way never expire, are are never "SecureOnly".
        """
        if self._last_request is None and (domain is None or path is None):
            raise ValueError("You must specify a domain and path for a \
                             new cookie if you haven't made a request \
                             (self.go()) yet.")

        if not domain:
            domain = ".%s" % urlparse(self._last_request.get_full_url())[1]

        if not path:
            path = urlparse(self._last_request.get_full_url())[2]

        self._cookiejar.set_cookie(cookielib.Cookie(
            0, key, value,
            None, False,
            domain, True, bool(domain[0] == '.'),
            path, True,
            secure=False,
            expires=None,
            discard=False,
            comment=None, comment_url=None,
            rest={}
            ))

    def remove_cookie(self, key=None, domain=None, path=None):
        """Removes a cookie from the underlying CookieJar instance.

        If only the domain is specified, all cookies for that domain will be removed.

        If only the domain and path are specified, all cookies for that path on that
        domain will be removed.

        If only the key is specified, the cookie with that key on the most recent request's
        domain and the most recent request's path will be removed.  If there have been no
        requests on this instance, an error will be thrown.

        Any other combination of arguments is an error.
        """
        if domain and not (path or key):
            self._cookiejar.clear(domain=domain)

        elif domain and path and not key:
            self._cookiejar.clear(domain=domain, path=path)

        elif domain and path and key:
            self._cookiejar.clear(domain=domain, path=path, name=key)

        elif key and not (domain or path) and self._last_request:
            parts = urlparse(self._last_request.get_full_url())
            self._cookiejar.clear(domain=parts[1], path=parts[2], name=key)

        else:
            raise ValueError("You called this method wrong, and I can't remove the cookies you think " \
                    "you are trying to tell me to remove.  Read `pydoc beautifulscraper.BeautifulScraper.remove_cookie`")

    def go(self, url, data=None, parser='html.parser',**kwargs):
        """Makes a request to url.  It will be a GET request unless you specify data, in
        which case it will be a POST request with data as a payload.  The any headers in
        self.headers will be a part of the request.  Any cookies that the CookieJar decides
        are approperate will also be a part of the request.

        self.response_headers will be populated with the headers from the server's response.

        self.response_code will be populated with the HTTP status code in the server's response.

        Any extra kwargs passed to this method will be passed to the underlying BeautifulSoup constructor.

        Returns a bs4.BeautifulSoup object initialized with the response body.
        """
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
        return BeautifulSoup(response.read(), parser, **kwargs)

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
                return urllib2.HTTPErrorProcessor.http_response(self,
                                                                request,
                                                                response)
        https_response = http_response
