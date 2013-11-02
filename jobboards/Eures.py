#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Bruno Adelé <bruno@adele.im>',
]
__license__ = 'GPLv2'
__version__ = '0.1'

# System
import os
import re
import time
import glob

# Third party
import sqlite3 as lite


from jobcatcher import JobCatcher
from jobcatcher import JobBoard
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


class JBEures(JobBoard):

    def __init__(self, rootdir='/tmp', configs=[], interval=1200):
        self.name = "Eures"
        super(JBEures, self).__init__(rootdir, configs, interval)



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
        # Refs
        self.datas['pageid'] = ""
        self.datas['ref'] = self._extractItem("Référence nationale", html)
        self.datas['nace'] = self._extractItem("Code Nace", html)

        # Dates
        self.datas['date_add'] = int(time.time()) 
        self.datas['date_pub'] = datetime.strptime(
            self._extractItem("Date de publication", html),
            "%d/%m/%Y").strftime('%s')

        # Job informations
        self.datas['title'] = self._extractItem("Titre", html)
        self.datas['location'] = self._extractItem("Région", html)
        self.datas['company'] = self._extractItem("Nom", html)
        self.datas['contract'] = self._extractItem("Type de contrat", html)
        # Salary
        self.datas['salary_min'] = self._extractItem("Salaire minimum", html)
        self.datas['salary_max'] = self._extractItem("Salaire maximum", html)
        self.datas['salary_period'] = self._extractItem("Période de rémunération", html)
        self.datas['nb_hours'] = self._extractItem("Horaire hebdomadaire", html)
        # Experiences
        self.datas['qualification'] = self._extractItem("Qualifications en formation exigées", html)
        self.datas['experience'] = self._extractItem("Expérience requise", html)

        # Insert to jobboard table
        self.insertToJBTable()
        #offer.add_db()



    def filterContract(self, offer):
        if 'PERMANENT' in offer.contract:
            offer.contract = 'CDI'

        if 'TEMPORAIRE' in offer.contract:
            offer.contract = 'CDD'

    def filterCompany(self, offer):
        if offer.company:
            m = re.search(r'([A-Z ]+)', offer.company, flags=re.MULTILINE | re.DOTALL)
            if m:
                offer.company = m.group(1)

    def createTable(self,):
        if self.isTableCreated():
            return

        conn = None
        conn = lite.connect("jobs.db")
        cursor = conn.cursor()

        # create a table
        cursor.execute("""CREATE TABLE jb_%s( \
                       ref TEXT, \
                       nace TEXT, \
                       pageid TEXT, \
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
                       PRIMARY KEY(ref))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect("jobs.db")
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" % 
                       self.name, (
                           self.datas['ref'],
                           self.datas['nace'],
                           self.datas['pageid'],
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
                       )
                   )
        conn.commit()
        if conn:
            conn.close()
        return 0

    def createOffer(self, data):
        """Create a offer object with jobboard data"""
        o = Offer()
        o.src = self.name
        o.ref = data['ref']
        o.title = data['title']
        o.company = data['company']
        o.contract = data['contract']
        o.location = data['location']
        o.salary = '%s - %s' % (data['salary_min'], data['salary_max'])
        o.date_pub = data['date_pub']
        o.date_add = data['date_add']

        return o
