#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
]
__license__ = 'GPLv2'
__version__ = '0.1'

# System
import re
import time
import glob
from datetime import datetime

# Third party
import sqlite3 as lite
from BeautifulSoup import BeautifulSoup

# Jobcatcher
import utilities
from jobcatcher import JobBoard
from jobcatcher import Offer


class JBRegionJob(JobBoard):

    def __init__(self, configs=[], interval=1200):
        self.name = "RegionJob"
        super(JBRegionJob, self).__init__(configs, interval)
        self.encoding = {'feed': 'utf-8', 'page': 'utf-8'}

    def getUrls(self):
        """Get Urls offers from feed"""

        urls = list()
        searchdir = "%s/feeds/*.feed" % self._processingDir

        for feed in glob.glob(searchdir):
            # Load the HTML feed
            utilities.openPage(feed)
            page = utilities.openPage(feed)
            feedid = page.pageid
            html = page.content

            # Search result
            res = re.finditer(
                r'<item>(.*?)</item>',
                html,
                flags=re.MULTILINE | re.DOTALL
            )
            for r in res:
                # Check if URL is valid
                m = re.search(r'<link>(.*?numoffre=.*?)</link>', r.group(1))
                if m:
                    urls.append([feedid, m.group(1)])

        return urls

    def _regexExtract(self, regex, soup):
        """Extract a field in html page"""

        html = unicode.join(u'\n', map(unicode, soup))

        res = None
        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = utilities.htmltotext(m.group(1)).strip()

        return res

    def _extractRubrique(self, field, soup):
        """Extract rubrique"""

        html = unicode.join(u'\n', map(unicode, soup))

        res = None
        regex = ur'<p class="rubrique_annonce">%s</p>.*?<p>(.*?)</p>' % field
        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = utilities.htmltotext(m.group(1)).strip()

        return res

    def analyzePage(self, page):
        """Analyze page and extract datas"""

        soup = BeautifulSoup(page.content, fromEncoding=self.encoding['page'])
        item = soup.body.find('div', attrs={'id': 'annonce'})

        if not item:
            return 1

        # Title
        h1 = item.find('h1')
        if not h1:
            return 1

        # Title & Url
        self.datas['title'] = utilities.htmltotext(h1.text).strip()
        self.datas['url'] = page.url

        # Date & Ref
        p = item.find('p', attrs={'class': 'date_ref'})
        if not p:
            return 1

        self.datas['ref'] = self._regexExtract(ur'Réf :(.*)', p)
        self.datas['feedid'] = page.feedid
        self.datas['date_add'] = int(time.time())
        self.datas['date_pub'] = datetime.strptime(
            self._regexExtract(ur'publié le(.*?)<br />', p),
            "%d/%m/%Y").strftime('%s')

        # Job informations
        p = item.find('p', attrs={'class': 'contrat_loc'})
        if not p:
            return 1

        # Location
        self.datas['department'] = None
        self.datas['location'] = self._regexExtract(
            ur'Localisation :.*?<strong>(.*?)</strong>', p
        )
        m = re.search('(.*?) - ([0-9]+)', self.datas['location'])
        if m:
            self.datas['location'] = m.group(1).strip()
            self.datas['department'] = m.group(2).strip()

        self.datas['company'] = self._regexExtract(
            ur'Entreprise :.*?<strong>(.*?)</strong>', p
        )
        if not self.datas['company']:
            self.datas['company'] = "NA"

        # Contract
        self.datas['duration'] = None
        self.datas['contract'] = self._regexExtract(
            ur'Contrat :.*?<strong>(.*?)</strong>', p
        )
        m = re.search('(.*?) - ([0-9]+ .*)', self.datas['contract'])
        if m:
            self.datas['contract'] = m.group(1).strip()
            text = m.group(2).strip()
            m = re.search('([0-9]+) (.*)', text)
            if m:
                number = m.group(1)
                if 'ans' in m.group(2):
                    self.datas['duration'] = int(number) * 12
                else:
                    self.datas['duration'] = number

        # Salary
        self.datas['salary'] = self._extractRubrique("Salaire", item)

        # Insert to jobboard table
        self.insertToJBTable()

    def createTable(self,):
        if self.isTableCreated():
            return

        conn = None
        conn = lite.connect(self.configs.globals['database'])
        cursor = conn.cursor()

        # create a table
        cursor.execute("""CREATE TABLE jb_%s( \
                       ref TEXT, \
                       feedid TEXT, \
                       url TEXT, \
                       date_pub INTEGER, \
                       date_add INTEGER, \
                       title TEXT, \
                       company TEXT, \
                       contract TEXT, \
                       duration INTEGER, \
                       location TEXT, \
                       department TEXT, \
                       salary TEXT, \
                       PRIMARY KEY(ref))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect(self.configs.globals['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?,?,?)" %
                           self.name, (
                               self.datas['ref'],
                               self.datas['feedid'],
                               self.datas['url'],
                               self.datas['date_pub'],
                               self.datas['date_add'],
                               self.datas['title'],
                               self.datas['company'],
                               self.datas['contract'],
                               self.datas['duration'],
                               self.datas['location'],
                               self.datas['department'],
                               self.datas['salary'],
                           )
            )

            conn.commit()
        except lite.IntegrityError:
            pass
        finally:
            if conn:
                conn.close()

        return 0

    def createOffer(self, data):
        """Create a offer object with jobboard data"""
        data = dict(data)

        o = Offer()
        o.src = self.name
        o.url = data['url']
        o.ref = data['ref']
        o.feedid = data['feedid']
        o.title = data['title']
        o.company = data['company']
        o.contract = data['contract']
        o.duration = data['duration']
        o.location = data['location']
        o.department = data['department']
        o.salary = data['salary']
        o.date_pub = data['date_pub']
        o.date_add = data['date_add']

        if o.ref and o.company:
            return o

        return None
