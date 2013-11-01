#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Bruno Adelé <bruno@adele.im>',
]
__license__ = 'GPLv2'
__version__ = '0.1'

import os
import re
import time
import glob

from jobcatcher import JobCatcher
from jobcatcher import Jobboard
from jobcatcher import Offer
from jobcatcher import Location
from config import configs
from html2text import html2text


from lxml import etree
from StringIO import StringIO
import sys

from xml.dom import minidom
from datetime import datetime
import utilities

from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup


class Eures(Jobboard):

    def __init__(self, configs=[]):
        self.name = "Eures"
        self._configs = configs
        self._processingDir = "%s/%s" % (
            self._configs['global']['rootdir'],
            self.name
        )

    def getUrls(self):
        """Get Urls offers from feed"""

        urls = list()
        searchdir = "%s/feeds/*.feed" % self._processingDir

        for feed in glob.glob(searchdir):
            # Load the HTML feed
            fd = open(feed, 'rb')
            html = fd.read()
            fd.close()

            # Search result
            res = re.finditer(
                r'<table class="JResult">.*?javascript:popUp\(\'(.*?)\'\);.*?</table>',
                html,
                flags=re.MULTILINE | re.DOTALL
            )
            for r in res:
                # Check if URL is valid
                m = re.match(r'\./ShowJvServlet\?lg=FR&pesId=[0-9]+&uniqueJvId=[0-9A-Z]+&nnImport=false', r.group(1))
                if m:
                    url = "http://ec.europa.eu/eures/eures-searchengine/servlet/%s" % r.group(1)
                    urls.append(url)

        return urls

    def _extractItem(self, itemname, html):
        """Extract a field in html page"""
        res = None
        regex = '<th.*?>%s:</th>.*?<td.*?>(.*?)</td>' % itemname

        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = html2text(m.group(1)).rstrip()

        return res

    def analyzePage(self, html):
        """Analyze page and extract datas"""
        # Extract datas
        offer = Offer()
        offer.src = self.name

        # Dates
        offer.date_add = int(time.time())
        offer.date_pub = datetime.strptime(
            self._extractItem("Date de publication", html),
            "%d/%m/%Y").strftime('%s')

        # Job informations
        offer.ref = self._extractItem("Référence nationale", html)
        offer.title = self._extractItem("Titre", html)
        offer.title = self._extractItem("Titre", html)
        offer.location = self._extractItem("Région", html)
        offer.company = self._extractItem("Nom", html)

        # contract
        offer.contract = self._extractItem("Type de contrat", html)
        self.filterContract(offer)

        # Salaries
        offer.salary = "%s - %s" % (
            self._extractItem("Salaire minimum", html),
            self._extractItem("Salaire maximum", html)
        )

        if offer.company:
            offer.add_db()

    def filterContract(self, offer):
        if 'PERMANENT' in offer.contract:
            offer.contract = 'CDI'

        if 'TEMPORAIRE' in offer.contract:
            offer.contract = 'CDD'
