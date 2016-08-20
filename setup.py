# Copyright (C) 2012 by Andrew Regner <andrew@aregner.com>
#
# beautifulscraper is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from setuptools import setup
import os

PARAMS = {}
PARAMS["name"] = "beautifulscraper"
PARAMS["version"] = "1.0.4"
PARAMS["description"] = \
        "Python web-scraping library that wraps urllib2 and BeautifulSoup."
PARAMS["long_description"] = \
        "Simple wraper around BeautifulSoup for HTML parsing and urllib2 for " \
        "HTTP(S) request/response handling.  BeautifulScraper also overrides " \
        "some of the default handlers in urllib2 in order to: handle cookies " \
        "properly, offer full control of included cookies, and return the " \
        "actual response from the server, un-mangled and not reprocessed"
PARAMS["author"] = "Andrew Regner"
PARAMS["author_email"] = "andrew@aregner.com"
PARAMS["url"] = "https://github.com/adregner/beautifulscraper"
PARAMS["license"] = "MIT"

PARAMS["install_requires"] = ["beautifulsoup4"]

PARAMS["packages"] = [
        PARAMS["name"],
        ]

try:
    os.link("README.md", "README")
except:
    pass

PARAMS["data_files"] = [
        ("share/doc/{P[name]}-{P[version]}".format(P = PARAMS), [
            "README",
            ]),
        ]

setup(**PARAMS)

