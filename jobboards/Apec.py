#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
    'Yankel Scialom <yankel.scialom@mail.com>'
]
__license__ = 'GPLv2'
__version__ = '0.1'

# System
import re
import sys
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

class JBApec(JobBoard):

    def __init__(self, configs=[], interval=1200):
        self.name = "Apec"
        super(JBApec, self).__init__(configs, interval)
        self.encoding = {'feed': 'utf-8', 'page': 'iso-8859-1'}

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
                m = re.search(r'<link>(http://cadres\.apec\.fr/offres-emploi-cadres/.*?)</link>', r.group(1))
                if m:
                    urls.append([feedid, m.group(1)])

        return urls

    def _extractItem(self, itemname, soup):
        """Extract a field in html page"""

        html = unicode.join(u'\n', map(unicode, soup))

        res = None
        regex = '<th.*?>%s :.*?</th>.*?<td.*?>(.*?)</td>' % itemname

        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = utilities.htmltotext(m.group(1)).strip()

        return res

    def _extractCompagny(self, soup):
        """Extract a field in html page"""

        html = unicode.join(u'\n', map(unicode, soup))

        res = None
        regex = u'<th valign="top">Société :</th>.*?<td>.*?<br />(.*?)<br />.*?</td>'

        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = utilities.htmltotext(m.group(1)).strip()

        return res


    def analyzePage(self, url, html):
        """Analyze page and extract datas"""

        soup = BeautifulSoup(html, fromEncoding=self.encoding['page'])
        item = soup.body.find('div', attrs={'class': 'boxMain boxOffres box'})

        if not item:
            content = item.find('p')
            if (content.text == u'L\'offre que vous souhaitez afficher n\'est plus disponible.Cliquer sur le bouton ci-dessous pour revenir à l\'onglet Mes Offres'):
                return 1

        # Title
        h1 = soup.body.find('h1', attrs={'class': 'detailOffre'})
        if not item:
            return 1

        self.datas['title'] = utilities.htmltotext(h1.text).replace('Détail de l\'offre : ', '').strip()

        # Refs
        table = item.find('table', attrs={'class': 'noFieldsTable'})
        if not table:
            return 1

        self.datas['url'] = url
        self.datas['ref'] = self._extractItem(u"Référence Apec", table)
        self.datas['refsoc'] = self._extractItem(u"Référence société", table)

        # Dates
        self.datas['date_add'] = int(time.time())
        self.datas['date_pub'] = datetime.strptime(
            self._extractItem("Date de publication", table),
            "%d/%m/%Y").strftime('%s')

        # Job informations
        self.datas['location'] = self._extractItem("Lieu", table)
        self.datas['company'] = self._extractCompagny(table)
        self.datas['contract'] = self._extractItem("Nombre de postes", table)
        # Salary
        self.datas['salary'] = self._extractItem("Salaire", table)
        # Experiences
        self.datas['experience'] = self._extractItem("Expérience", table)

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
                       refsoc TEXT, \
                       url TEXT, \
                       date_pub INTEGER, \
                       date_add INTEGER, \
                       title TEXT, \
                       company TEXT, \
                       contract TEXT, \
                       location TEXT, \
                       salary TEXT, \
                       experience TEXT, \
                       PRIMARY KEY(ref))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect(self.configs.globals['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?,?)" % 
                           self.name, (
                               self.datas['ref'],
                               self.datas['refsoc'],
                               self.datas['url'],
                               self.datas['date_pub'],
                               self.datas['date_add'],
                               self.datas['title'],
                               self.datas['company'],
                               self.datas['contract'],
                               self.datas['location'],
                               self.datas['salary'],
                               self.datas['experience'],
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
        o.salary = data['salary']
        o.date_pub = data['date_pub']
        o.date_add = data['date_add']

        if o.ref and o.company:
            return o

        return None
