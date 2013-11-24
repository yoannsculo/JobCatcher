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

# Jobcatcher
import utilities
from jc.data import Offer
from jc.jobboard import JobBoard


class JBEures(JobBoard):

    def __init__(self, configs=[]):
        self.name = "Eures"
        super(JBEures, self).__init__(configs)

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
                r'<table class="JResult">.*?javascript:popUp\(\'(.*?)\'\);.*?</table>',
                html,
                flags=re.MULTILINE | re.DOTALL
            )
            for r in res:
                # Check if URL is valid
                m = re.match(r'\./ShowJvServlet\?lg=FR&pesId=[0-9]+&uniqueJvId=[0-9A-Z]+&nnImport=false', r.group(1))
                if m:
                    url = "http://ec.europa.eu/eures/eures-searchengine/servlet/%s" % r.group(1)
                    urls.append([feedid, url])

        return urls

    def _extractItem(self, itemname, html):
        """Extract a field in html page"""
        res = None
        regex = '<th.*?>%s:</th>.*?<td.*?>(.*?)</td>' % itemname

        m = re.search(regex, html, flags=re.MULTILINE | re.DOTALL)
        if m:
            res = utilities.htmltotext(m.group(1)).rstrip()

        return res

    def extractOfferId(self, page):
        offerid = None
        m = re.search(
            ur'.*?uniqueJvId=(.*?)&.*',
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

        # Refs
        self.datas['url'] = page.url
        self.datas['offerid'] = self.extractOfferId(page)
        self.datas['lastupdate'] = page.lastupdate
        self.datas['ref'] = self._extractItem("Référence nationale", page.content)
        self.datas['feedid'] = page.feedid
        self.datas['nace'] = self._extractItem("Code Nace", page.content)

        # Dates
        self.datas['date_add'] = int(time.time())

        self.datas['date_pub'] = self._extractItem("Date de publication", page.content)
        if self.datas['date_pub']:
            self.datas['date_pub'] = datetime.strptime(
                self.datas['date_pub'],
                "%d/%m/%Y").strftime('%s')

        # Job informations
        self.datas['title'] = self._extractItem("Titre", page.content)
        self.datas['location'] = self._extractItem("Région", page.content)
        self.datas['company'] = self._extractItem("Nom", page.content)
        if not self.datas['company']:
            self.datas['company'] = "NA"

        self.datas['contract'] = self._extractItem("Type de contrat", page.content)
        # Salary
        self.datas['salary_min'] = self._extractItem("Salaire minimum", page.content)
        self.datas['salary_max'] = self._extractItem("Salaire maximum", page.content)
        self.datas['salary_period'] = self._extractItem("Période de rémunération", page.content)
        self.datas['nb_hours'] = self._extractItem("Horaire hebdomadaire", page.content)
        # Experiences
        self.datas['qualification'] = self._extractItem("Qualifications en formation exigées", page.content)
        self.datas['experience'] = self._extractItem("Expérience requise", page.content)

        # Insert to jobboard table
        self.datas['state'] = 'ACTIVE'
        self.insertToJBTable()

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
                       nace TEXT, \
                       url TEXT, \
                       date_pub INTEGER, \
                       date_add INTEGER, \
                       title TEXT, \
                       company TEXT, \
                       contract TEXT, \
                       location TEXT, \
                       salary_min TEXT, \
                       salary_max TEXT, \
                       salary_period TEXT, \
                       nb_hours TEXT, \
                       qualification TEXT, \
                       experience TEXT, \
                       state TEXT, \
                       PRIMARY KEY(offerid))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect(self.configs.globals['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" % 
                           self.name, (
                               self.datas['offerid'],
                               self.datas['lastupdate'],
                               self.datas['ref'],
                               self.datas['feedid'],
                               self.datas['nace'],
                               self.datas['url'],
                               self.datas['date_pub'],
                               self.datas['date_add'],
                               self.datas['title'],
                               self.datas['company'],
                               self.datas['contract'],
                               self.datas['location'],
                               self.datas['salary_min'],
                               self.datas['salary_max'],
                               self.datas['salary_period'],
                               self.datas['nb_hours'],
                               self.datas['qualification'],
                               self.datas['experience'],
                               self.datas['state'],

                           )
                       )
            conn.commit()
        except lite.IntegrityError:
            pass
        finally:
            if conn:
                conn.close()

    def createOffer(self, data):
        """Create a offer object with jobboard data"""
        data = dict(data)
        self.filterAllFields(data)

        o = Offer()
        o.src = self.name
        o.offerid = data['offerid']
        o.lastupdate = data['lastupdate']
        o.url = data['url']
        o.ref = data['ref']
        o.feedid = data['feedid']
        o.title = data['title']
        o.company = data['company']
        o.contract = data['contract']
        o.location = data['location']
        o.salary = data['salary']
        o.date_pub = data['date_pub']
        o.date_add = data['date_add']
        o.state = data['state']

        if o.offerid and o.ref and o.company:
            return o

        return None

    def filterAllFields(self, data):
        self.filterContract(data)
        self.filterCompany(data)
        self.filterSalaries(data)

    def filterSalaries(self, data):
        data['salary'] = ""

        # Min
        if data['salary_min']:
            data['salary_min'] = re.sub(r',', '', data['salary_min'])
            data['salary_min'] = re.sub(r'(\.[0-9]+)', r'\1 €', data['salary_min'])
        else:
            data['salary_min'] = ""

        # Max
        if data['salary_max']:
            data['salary_max'] = re.sub(r',', '', data['salary_max'])
            data['salary_max'] = re.sub(r'(\.[0-9]+)', r'\1 €', data['salary_max'])
        else:
            data['salary_max'] = ""

        if data['salary_min'] and data['salary_max']:
            data['salary'] = '%s - %s' % (data['salary_min'], data['salary_max'])
        else:
            if data['salary_min']:
                data['salary'] = data['salary_min']
            else:
                data['salary'] = data['salary_max']

    def filterContract(self, data):
        if data['contract']:
            # CDI, CDD
            data['contract'] = re.sub(r'PERMANENT \+ ', 'CDI', data['contract'])
            data['contract'] = re.sub(r'TEMPORAIRE \+ ', 'CDD', data['contract'])

            #Mi-temps,
            data['contract'] = re.sub(r'TEMPS PARTIEL', ', TEMPS PARTIEL', data['contract'])
            data['contract'] = re.sub(r'TEMPS PLEIN', '', data['contract'])

    def filterCompany(self, data):
        if data['company']:
            data['company'] = re.sub(r'M\. .*', '', data['company'])
            data['company'] = re.sub(r'Mme .*', '', data['company'])
