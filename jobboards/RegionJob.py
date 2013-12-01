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
from jc.data import Offer
from jc.jobboard import JobBoard


class JBRegionJob(JobBoard):

    def __init__(self, configs=[]):
        self.name = "RegionJob"
        super(JBRegionJob, self).__init__(configs)
        self.encoding = {'feed': 'utf-8', 'page': 'utf-8'}

    def getUrls(self):
        """Get Urls offers from feed"""

        urls = list()
        searchdir = "%s/feeds/*.feed" % self._processingDir

        for feed in glob.glob(searchdir):
            # Load the HTML feed
            page = utilities.openPage(feed)

            if page:
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

    def extractOfferId(self, page):
        offerid = None
        m = re.search(
            ur'.*?numoffre=([0-9]+)&amp;.*',
            page.url,
            flags=re.MULTILINE | re.DOTALL
        )
        if m:
            offerid = m.group(1)

        return offerid

    def analyzePage(self, page):
        """Analyze page and extract datas"""

        if not self.requireAnalyse(page):
            return ""

        self.datas['offerid'] = self.extractOfferId(page)
        soup = BeautifulSoup(page.content, fromEncoding=self.encoding['page'])
        item = soup.body.find('div', attrs={'id': 'annonce'})

        if not item:
            self.disableOffer(self.datas['offerid'])
            return ""

        # Title
        h1 = item.find('h1')
        if not h1:
            return "No title found"

        # Title & Url
        self.datas['title'] = utilities.htmltotext(h1.text).strip()
        self.datas['url'] = page.url

        # Date & Ref
        p = item.find('p', attrs={'class': 'date_ref'})
        if not p:
            return "No date section found"

        self.datas['offerid'] = self.extractOfferId(page)
        self.datas['lastupdate'] = page.lastupdate
        self.datas['ref'] = self._regexExtract(ur'Réf :(.*)', p)
        self.datas['feedid'] = page.feedid
        self.datas['date_add'] = int(time.time())
        self.datas['date_pub'] = datetime.strptime(
            self._regexExtract(ur'publié le(.*?)<br />', p),
            "%d/%m/%Y").strftime('%s')

        # Job informations
        p = item.find('p', attrs={'class': 'contrat_loc'})
        if not p:
            return "No job information found"

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
        self.filterSalaries(self.datas)

        # Insert to jobboard table
        self.datas['state'] = 'ACTIVE'
        self.insertToJBTable()

        return None

    def createTable(self,):
        if self.isTableCreated():
            return

        conn = None
        conn = lite.connect(self.configs.globals['database'])
        cursor = conn.cursor()

        # create a table
        cursor.execute("""CREATE TABLE jb_%s( \
                       offerid TEXT, \
                       lastupdate INTEGER, \
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
                       salary_min FLOAT, \
                       salary_max FLOAT, \
                       salary_nbperiod INTEGER, \
                       salary_unit FLOAT, \
                       salary_bonus TEXT, \
                       salary_minbonus FLOAT, \
                       salary_maxbonus FLOAT, \
                       state TEXT, \
                       PRIMARY KEY(offerid))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect(self.configs.globals['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" %
                           self.name, (
                               self.datas['offerid'],
                               self.datas['lastupdate'],
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
                               self.datas['salary_min'],
                               self.datas['salary_max'],
                               self.datas['salary_nbperiod'],
                               self.datas['salary_unit'],
                               self.datas['salary_bonus'],
                               self.datas['salary_minbonus'],
                               self.datas['salary_maxbonus'],
                               self.datas['state'],

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
        o.offerid = data['offerid']
        o.lastupdate = data['lastupdate']
        o.ref = data['ref']
        o.feedid = data['feedid']
        o.title = data['title']
        o.company = data['company']
        o.contract = data['contract']
        o.duration = data['duration']
        o.location = data['location']
        o.department = data['department']
        o.salary = data['salary']
        o.salary_min = data['salary_min']
        o.salary_max = data['salary_max']
        o.salary_unit = data['salary_unit']
        o.salary_nbperiod = data['salary_nbperiod']
        o.salary_bonus = data['salary_bonus']
        o.salary_minbonus = data['salary_minbonus']
        o.salary_maxbonus = data['salary_maxbonus']
        o.date_pub = data['date_pub']
        o.date_add = data['date_add']
        o.state = data['state']

        if o.offerid and o.ref and o.company:
            return o

        return None

    def filterSalaries(self, data):
        minbonus = 0
        maxbonus = 0

        if self.datas['salary']:
            # Salary
            self.datas['salary_unit'] = ''
            self.datas['salary_min'] = 0
            self.datas['salary_max'] = 0
            self.datas['salary_nbperiod'] = 0
            # Bonus
            self.datas['salary_bonus'] = ''
            self.datas['salary_minbonus'] = 0
            self.datas['salary_maxbonus'] = 0

            # Search salary range
            m = re.search(
                ur'([0-9]+)/([0-9]+).*par mois sur (.*?) mois\.?(.*)',
                self.datas['salary'],
                flags=re.MULTILINE | re.DOTALL
            )
            found = False
            if m:
                found = True
                self.datas['salary_unit'] = 1
                self.datas['salary_min'] = m.group(1)
                self.datas['salary_max'] = m.group(2)
                self.datas['salary_nbperiod'] = int(m.group(3))
                self.datas['salary_bonus'] = m.group(4)

            if not found:
                m = re.search(
                    ur'.*?([0-9]+) à ([0-9]+) Euros\.?(.*)',
                    self.datas['salary'],
                    flags=re.MULTILINE | re.DOTALL
                )
                found = False
                if m:
                    found = True
                    self.datas['salary_unit'] = 1
                    self.datas['salary_min'] = m.group(1)
                    self.datas['salary_max'] = m.group(2)
                    self.datas['salary_nbperiod'] = 12
                    self.datas['salary_bonus'] = m.group(3)

            if not found:
                m = re.search(
                    ur'.*?([0-9]+) à ([0-9]+) KEuros\.?(.*)',
                    self.datas['salary'],
                    flags=re.MULTILINE | re.DOTALL
                )
                found = False
                if m:
                    found = True
                    self.datas['salary_unit'] = 1
                    self.datas['salary_min'] = m.group(1)
                    self.datas['salary_max'] = m.group(2)
                    self.datas['salary_nbperiod'] = 12
                    self.datas['salary_bonus'] = m.group(3)

            if not found:
                m = re.search(
                    ur'([0-9]+)/([0-9]+) KE(uros)?(.*)',
                    self.datas['salary'],
                    flags=re.MULTILINE | re.DOTALL
                )
                found = False
                if m:
                    found = True
                    self.datas['salary_unit'] = 12
                    self.datas['salary_min'] = "%s000" % m.group(1)
                    self.datas['salary_max'] = "%s000" % m.group(2)
                    self.datas['salary_nbperiod'] = 12
                    self.datas['salary_bonus'] = m.group(4)

            if not found:
                m = re.search(
                    ur'.*?([0-9]+)-([0-9]+) KE(uros)?(.*)',
                    self.datas['salary'],
                    flags=re.MULTILINE | re.DOTALL
                )
                found = False
                if m:
                    found = True
                    self.datas['salary_unit'] = 12
                    self.datas['salary_min'] = "%s000" % m.group(1)
                    self.datas['salary_max'] = "%s000" % m.group(2)
                    self.datas['salary_nbperiod'] = 12
                    self.datas['salary_bonus'] = m.group(4)

            if found:
                # Format
                self.datas['salary_min'] = float(
                    re.sub(
                        r'[\W_]',
                        '',
                        self.datas['salary_min']
                    )
                )
                self.datas['salary_max'] = float(
                    re.sub(
                        r'[\W_]',
                        '',
                        self.datas['salary_max']
                    )
                )

            if not found:
                # Search salary
                m = re.search(
                    ur'(.*?) Euros(/mois)?\.(.*)',
                    self.datas['salary'],
                    flags=re.MULTILINE | re.DOTALL
                )
                if m:
                    found = True
                    self.datas['salary_unit'] = 1
                    self.datas['salary_min'] = m.group(1)
                    self.datas['salary_max'] = 0
                    self.datas['salary_nbperiod'] = 12
                    self.datas['salary_bonus'] = m.group(3)

                # Format
                if found:
                    self.datas['salary_min'] = float(
                        re.sub(
                            r'[\W_]',
                            '',
                            self.datas['salary_min']
                        )
                    )

            if self.datas['salary_unit'] == 'Annuel':
                self.datas['salary_unit'] = 12
            elif self.datas['salary_unit'] == 'Mensuel':
                self.datas['salary_unit'] = 1
