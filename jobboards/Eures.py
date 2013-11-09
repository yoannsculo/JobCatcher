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
from html2text import html2text

# Jobcatcher
from jobcatcher import JobBoard
from jobcatcher import Offer


class JBEures(JobBoard):

    def __init__(self, configs=[], interval=1200):
        self.name = "Eures"
        super(JBEures, self).__init__(configs, interval)

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

    def analyzePage(self, url, html):
        """Analyze page and extract datas"""
        # Refs
        self.datas['url'] = url
        self.datas['ref'] = self._extractItem("Référence nationale", html)
        self.datas['nace'] = self._extractItem("Code Nace", html)

        # Dates
        self.datas['date_add'] = int(time.time())

        self.datas['date_pub'] = self._extractItem("Date de publication", html)
        if self.datas['date_pub']:
            self.datas['date_pub'] = datetime.strptime(
                self.datas['date_pub'],
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

    def createTable(self,):
        if self.isTableCreated():
            return

        conn = None
        conn = lite.connect(self.configs['global']['database'])
        cursor = conn.cursor()

        # create a table
        cursor.execute("""CREATE TABLE jb_%s( \
                       ref TEXT, \
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
                       PRIMARY KEY(ref))""" % self.name)

    def insertToJBTable(self):
        conn = lite.connect(self.configs['global']['database'])
        conn.text_factory = str
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO jb_%s VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" % 
                           self.name, (
                               self.datas['ref'],
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
