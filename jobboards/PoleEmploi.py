#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
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


class JBPoleEmploi(JobBoard):

    def __init__(self, configs=None, interval=1200):
        self.name = "PoleEmploi"
        super(JBPoleEmploi, self).__init__(configs, interval)
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
                r'<tr.*?>(.*?)</tr>',
                html,
                flags=re.MULTILINE | re.DOTALL
            )
            for r in res:
                # Check if URL is valid
                m = re.search(r'href="\./resultats\.tableauresultatrechercheoffre:detailOffre/(.*?)"', r.group(1))
                if m:
                    url = "http://candidat.pole-emploi.fr/candidat/rechercheoffres/detail/%s" % m.group(1)
                    urls.append([feedid, url])

        return urls

    def _regexExtract(self, text, soup):
        """Extract a field in html page"""

        html = unicode.join(u'\n', map(unicode, soup))
        regex='<div class="label"><span>%s</span></div>.*?<div class="value"><span.*?>(.*?)</span></div>' % text
        res = None
        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = utilities.htmltotext(m.group(1)).strip()

        return res

    def analyzePage(self, url, html):
        """Analyze page and extract datas"""

        soup = BeautifulSoup(html, fromEncoding=self.encoding['page'])
        item = soup.body.find('div', attrs={'class': 'block-content'})

        if not item:
            return 1

        # Title
        h4 = item.find('h4', attrs={'itemprop': 'title'})
        if not h4:
            return 1

        # Title & Url
        self.datas['title'] = utilities.htmltotext(h4.text).strip()
        self.datas['url'] = url

        # Ref
        li = item.find('li', attrs={'class': 'primary'})
        self.datas['ref'] = self._regexExtract(u'Numéro de l\'offre', li)

        li = item.find('li', attrs={'class': 'secondary'})
        if not li:
            return 1

        # Date
        self.datas['date_add'] = int(time.time())
        self.datas['date_pub'] = datetime.strptime(
            self._regexExtract(u'Offre actualisée le', li),
            "%d/%m/%Y").strftime('%s')

        # Job informations
        self.datas['contract'] = self._regexExtract(
            u'Type de contrat', item
        )
        self.datas['salary'] = self._regexExtract(
            u'Salaire indicatif', item
        )

        # Location
        li = item.find('li', attrs={'itemprop': 'addressRegion'})
        if not li:
            return 1

        self.datas['department'] = None
        self.datas['location'] = li.text.strip()
        m = re.search('([0-9]+) - (.*)', self.datas['location'])
        if m:
            self.datas['department'] = m.group(1).strip()
            self.datas['location'] = m.group(2).strip()

        # Compagny
        p = item.find('p', attrs={'itemprop': 'hiringOrganization'})
        if not p:
            return 1
        self.datas['company'] = p.text.strip()

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
                       url TEXT, \
                       date_pub INTEGER, \
                       date_add INTEGER, \
                       title TEXT, \
                       company TEXT, \
                       contract TEXT, \
                       location TEXT, \
                       department TEXT, \
                       salary TEXT, \
                       PRIMARY KEY(ref))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect(self.configs.globals['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?)" %
                           self.name, (
                               self.datas['ref'],
                               self.datas['url'],
                               self.datas['date_pub'],
                               self.datas['date_add'],
                               self.datas['title'],
                               self.datas['company'],
                               self.datas['contract'],
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
        o.title = data['title']
        o.company = data['company']
        o.contract = data['contract']
        o.location = data['location']
        o.department = data['department']
        o.salary = data['salary']
        o.date_pub = data['date_pub']
        o.date_add = data['date_add']

        if o.ref and o.company:
            return o

        return None
