BeautifulScraper
----------------

Simple wraper around [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) for HTML parsing and urllib2 for HTTP(S) request/response handling.  BeautifulScraper also overrides some of the default handlers in [urllib2](http://docs.python.org/2/library/urllib2.html) in order to:
  * Handle cookies properly
  * Offer full control of included cookies
  * Return the actual response from the server, un-mangled and not reprocessed

Installation
------------

    # pip install beautifulscraper

or

    # git clone git://github.com/adregner/beautifulscraper.git
    # cd beautifulscraper/
    # python setup.py install

Examples
--------

Getting started is brain-dead simple.
```python
>>> from beautifulscraper import BeautifulScraper
>>> scraper = BeautifulScraper()
```

Start by requesting something.
```python
>>> body = scraper.go("https://github.com/adregner/beautifulscraper")
```

The response will be a plain BeautifulSoup object.  See [their documentation](http://www.crummy.com/software/BeautifulSoup/bs4/doc/) for how to use it.
```python
>>> body.select(".repository-meta-content")[0].text
'\n\n            Python web-scraping library that wraps urllib2 and BeautifulSoup\n          \n'
```

The headers from the server's response are accessiable.
```python
>>> for header, value in scraper.response_headers.items():
...     print "%s: %s" % (header, value)
...
status: 200 OK
content-length: 36179
set-cookie: _gh_sess=BAh7BzoQX2NzcmZfdG9rZW4iMUNCOWxnbFpVd3EzOENqVk9GTUFXbDlMVUJIbGxsNEVZUFZJNiswRjhwejQ9Og9zZXNzaW9uX2lkIiUyNmQ2ODE5ZDdiZjM3MTA2N2VlZDk3Y2VlMDViYzI2OA%3D%3D--5d31df13d5c0eeb8f3cccb140392124968abc374; path=/; expires=Sat, 01-Jan-2022 00:00:00 GMT; secure; HttpOnly
strict-transport-security: max-age=2592000
connection: close
server: nginx
x-runtime: 98
etag: "1c595b5b6a25eb7f021e68c3476d61da"
cache-control: private, max-age=0, must-revalidate
date: Wed, 31 Oct 2012 02:14:08 GMT
x-frame-options: deny
content-type: text/html; charset=utf-8
```

So is the response code as an integer.
```python
>>> type(scraper.response_code), scraper.response_code
(<type 'int'>, 200)
```

The scraper will keep track of all cookies it sees via the [cookielib.CookieJar class](http://docs.python.org/2/library/cookielib.html#cookiejar-and-filecookiejar-objects).  You can read the cookies if you'd like.  The [Cookie object](http://docs.python.org/2/library/cookielib.html#cookie-objects)'s are just a collection of properties.
```python
>>> scraper.cookies[0].name
'_gh_sess'
```

See the pydoc for more information.

