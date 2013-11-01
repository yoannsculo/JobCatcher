#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Yoann Sculo <yoann.sculo@gmail.com>'
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '1.0'

import os
import sys
import glob
import datetime
import codecs
import html2text
import requests
import importlib


from optparse import OptionParser
from xml.dom import minidom
import utilities
import sqlite3 as lite

reload(sys)
sys.setdefaultencoding("utf-8")

from config import configs


class FeedDownloader(object):
    """A class for dowload a feed or a HTML page"""

    def __init__(self, rootdir='/tmp', configs=[], interval=1200):
        self._rootdir = rootdir
        self._configs = configs
        self._interval = interval

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter  
    def rootdir(self, value):
        self._rootdir = value

    @property
    def interval(self):
        """Get interval in minute"""
        return self._interval

    @rootdir.setter  
    def interval(self, value):
        """Set interval in minute"""
        self._interval = value

    @property
    def configs(self):
        return self._configs

    @rootdir.setter
    def configs(self, value):
        self._configs = value

    def downloadFeeds(self, forcedownload=False):
        """Download all feeds or HTMLs pages"""
        for jobboardname in self._configs:
            if jobboardname not in self._configs['global']['ignorejobboard']:
                if 'feeds' in self._configs[jobboardname]:
                    feeds = self._configs[jobboardname]['feeds']

                    # Donwload all feeds for jobboard
                    for url in feeds:
                        self.downloadFeed(jobboardname, url, forcedownload)

    def downloadFeed(self, jobboardname, url, forcedownload=False):
        """Download a feed or a HTML page"""

        destdir = "%s/%s/feeds" % (self.rootdir, jobboardname)
        md5 = utilities.md5(url)
        saveto = "%s/%s.feed" % (destdir, md5)
        utilities.downloadFile(
            url, saveto, self._interval)

    def downloadPages(self, jobboardname, urls):
        """Download all pages from urls list"""
        destdir = "%s/%s/pages" % (self.rootdir, jobboardname)

        for u in urls:
            md5 = utilities.md5(u)
            saveto = "%s/%s.page" % (destdir, md5)
            utilities.downloadFile(u, saveto, self._interval)

    def analyzesPages(self):
        """Analyze downloaded pages"""
        for jobboardname in self._configs:
            if jobboardname not in self._configs['global']['ignorejobboard']:
                if 'feeds' in self._configs[jobboardname]:
                    module = importlib.import_module(
                        'jobboards.%s' % jobboardname
                    )
                    moduleClass = getattr(module, jobboardname)
                    plugin = moduleClass(configs)

                    destdir = "%s/%s/pages" % (self.rootdir, jobboardname)
                    for p in glob.glob("%s/*.page" % destdir):
                        # Load the HTML feed
                        fd = open(p, 'rb')
                        html = fd.read()
                        fd.close()

                        plugin.analyzePage(html)

class Jobboard():
    name = ''
    url = ''
    lastFetch = ''
    dlDir = "./dl"

    def load(self, file):
        ""

    def fetch(self):
        ""

    def fetch_offer(self, url):
        ""

    def fetch_url(self, url):
        ""

    def processOffers(self):
        for file in os.listdir(self.processingDir):
            ret = self.processOffer(file)

    def processOffer(self, file):
        ""

    def fetchAllOffersFromDB(self):
        conn = lite.connect("jobs.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM offers WHERE source='%s' ORDER BY date_pub DESC" %(self.name)
        cursor.execute(sql)
        data = cursor.fetchall()
        return data

class Location():

    lon = "0"
    lat = "0"

    def loadFromAddress(self, address):
        r = requests.get("http://nominatim.openstreetmap.org/search",
                params={'q': address,
                        'format':'xml',
                        'polygon': 0,
                        'addressdetails': 1})
        if (r.status_code != 200):
            return

        xmldoc = minidom.parseString(r.content)
        if (xmldoc.getElementsByTagName('place').length <= 0):
            return

        res = xmldoc.getElementsByTagName('place')[0]
        self.lat = res.getAttribute('lat')
        self.lon = res.getAttribute('lon')


class Offer():
    def __init__(self):
        self.ref = u""
        self.title = u""
        self.company = u""
        self.contract = u""
        self.location = u""
        self.salary = u""
        self.url = u""
        self.content = u""
        self.date_add = u""
        self.date_pub = u""
        self.lat = u""
        self.lon = u""

    def load(
            self, src, ref, date_pub, date_add, title, company,
            contract, location, lat, lon, salary, url, content
    ):

        self.src = src
        self.ref = ref

        self.date_pub = datetime.datetime.fromtimestamp(int(date_pub))
        self.date_add = datetime.datetime.fromtimestamp(int(date_add))
        self.title = title
        self.company = company
        self.contract = contract
        self.location = location
        self.salary = salary
        self.url = url
        self.content = content

    def loadFromHtml(self, filename):
        ""

    def cleanContract(self):
        self.contract = utilities.filter_contract_fr(self.contract)
        return

    def cleanLocation(self):
        self.location = utilities.filter_location_fr(self.location)
        return

    def cleanSalary(self):
        self.salary = utilities.filter_salary_fr(self.salary)
        return

    def add_db(self):
        return utilities.db_add_offer(self)

    def printElt(self):
        #print "Title :" + self.title
        print "Company : " + self.company

    #def set_from_row(row):
    #    self.src = row[0]
    #    self.ref = row[1]
    #    self.date_pub = datetime.datetime.fromtimestamp(int(row[2]))
    #    self.date_add = datetime.datetime.fromtimestamp(int(row[3]))
    #    self.title = row[4].encode("utf-8")
    #    self.company = row[5].encode("utf-8")
    #    self.contract = row[6].encode("utf-8")
    #    self.location = row[7].encode("utf-8")
    #    self.salary = row[8].encode("utf-8")
    #    self.url = row[9].encode("utf-8")
    #    self.content = row[10].encode("utf-8")


class JobCatcher():

    jobBoardList = []

    def loadPlugins(self):
        """ load all jobboards from jobboards directory
        """

        for file in glob.glob("./jobboards/*.py"):
            name = os.path.splitext(os.path.basename(file))[0]
            if name != "Eures":
                continue
            if (name == '__init__'):
                continue

            module = importlib.import_module('jobboards.'+name);
            moduleClass = getattr(module, name)
            instance = moduleClass(configs)
            self.jobBoardList.append(instance)

    def run(self):
        fd = FeedDownloader(configs['global']['rootdir'])
        fd.configs = configs

        for jobboard in self.jobBoardList:
            if jobboard.name not in configs['global']['ignorejobboard']:
                if jobboard.name != "Eures":
                    continue

                print ""
                print "=================================="
                print jobboard.name
                print "=================================="

                urls = jobboard.getUrls()
                fd.downloadPages(jobboard.name, urls)
                sys.exit()

                if configs['global']['debug']:
                    jobboard.fetch()
                else:
                    try:
                        jobboard.fetch()
                    except:
                        print "Ignored (parsing error)."


def initblacklist():
    utilities.blacklist_flush()
    utilities.blocklist_load()


def feeddownload():
    fd = FeedDownloader(configs['global']['rootdir'])
    fd.configs = configs
    fd.downloadFeeds()


def pagesdownload():
    bot = JobCatcher()
    bot.loadPlugins()
    bot.run()


def pagesinsert():
    fd = FeedDownloader(configs['global']['rootdir'])
    fd.configs = configs
    fd.analyzesPages()


if __name__ == '__main__':
    parser = OptionParser(usage = 'syntax: %prog [options] <from> [to]')
    args = sys.argv[1:]

    parser.set_defaults(version = False)
    parser.add_option('-v', '--version',
                          action = 'store_true', dest = 'version',
                          help = 'Output version information and exit')
    parser.add_option('-r', '--report',
                          action = 'store_true', dest = 'report',
                          help = 'Generate a full report')
    parser.add_option('-a', '--all',
                          action = 'store_true', dest = 'all',
                          help = 'Sync the blacklist, fetch the offers and generates reports.')
    parser.add_option('-c', '--create',
                          action = 'store_true', dest = 'create',
                          help = 'create the databse')
    parser.add_option('-s', '--start',
                          action = 'store_true', dest = 'start',
                          help = 'start the fetch')
    parser.add_option('-p', '--pages',
                          action = 'store_true', dest = 'pages',
                          help = 'Pages download')
    parser.add_option('-i', '--insert',
                          action = 'store_true', dest = 'insert',
                          help = 'Insert pages')
    # parser.add_option('-b', '--blocklist',
    #                       action = 'store_true', dest = 'blocklist',
    #                       help = 'update blocklist')
    parser.add_option('-u', '--url',
                          action = 'store_true', dest = 'url',
                          help = 'analyse an url')
    parser.add_option('-f', '--flush',
                          action = 'store_true', dest = 'flush',
                          help = 'flush the blacklist and update it.')

    (options, args) = parser.parse_args(args)

    if options.version:
        print 'jobcatcher version %s - %s (%s)' % (__version__,
                                                __copyright__,
                                                __license__)
        sys.exit(0)

    if options.report:
        print "Report generation..."
        utilities.report_generate(True)
        utilities.report_generate(False)
        utilities.statistics_generate()
        print "Done."
        sys.exit(0)

    # if options.add:
    #     if len(args) == 11:
    #         print "%s" % args[10]
    #         offer = Offer()
    #         offer.load(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], args[10])
    #         db_add_offer(offer)

    #     sys.exit(0)

    if options.all:
        initblacklist()
        feeddownload()
        pagesdownload()
        utilities.report_generate(True)
        utilities.report_generate(False)
        utilities.statistics_generate()
        sys.exit(0)

    if options.url:
        if len(args) != 1:
            print "error"
        else:
            import importlib
            module = importlib.import_module('jobboards.Apec');
            moduleClass = getattr(module, 'Apec')
            instance = moduleClass()
            filename = instance.fetch_offer(args[0])
            instance.processOffer(filename)
        sys.exit(0)

    if options.create:
        utilities.db_create()
        sys.exit(0)

    if options.start:
        print "Try to load a feed"
        feeddownload()
        print "Done."
        sys.exit(0)

    if options.pages:
        pagesdownload()
        sys.exit(0)

    if options.insert:
        pagesinsert()
        sys.exit(0)

    if options.blocklist:
        utilities.blocklist_load();
        sys.exit(0)

    if options.flush:
        initblacklist()
        sys.exit(0)
