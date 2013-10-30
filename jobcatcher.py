#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Yoann Sculo <yoann.sculo@gmail.com>'
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '1.0'

import os
import sys
import datetime
import codecs
import html2text
import requests

from optparse import OptionParser
from xml.dom import minidom
import utilities
import sqlite3 as lite

reload(sys)
sys.setdefaultencoding("utf-8")

from config import configs


class FeedDownloader(object):
    """A class for dowload a feed or a HTML page"""

    def __init__(self, rootdir='/tmp', configs = [], interval = 20):
        self._rootdir = rootdir
        self._configs = configs
        self._interval = interval * 60

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter  
    def rootdir(self, value):
        self._rootdir = value

    @property
    def interval(self):
        return self._interval

    @rootdir.setter  
    def interval(self, value):
        self._interval = value * 60

    @property
    def configs(self):
        return self._configs

    @rootdir.setter
    def configs(self, value):
        self._configs = value

    def downloads(self, forcedownload=False):
        """Download all feeds or HTMLs pages"""
        for j in self._configs:
            if j not in self._configs['global']['ignorejobboard']:
                if 'feeds' in self._configs[j]:
                    feeds = self._configs[j]['feeds']

                    # Donwload all feeds for jobboard
                    for url in feeds:
                        self.downloadFeed(j, url, forcedownload)

    def downloadFeed(self, jobboardname, url, forcedownload=False):
        """Download a feed or a HTML page"""

        destdir = "%s/%s" % (self.rootdir, jobboardname)
        md5 = utilities.md5(url)
        saveto = "%s/%s.feed" % (destdir, md5)

        # Check if i must download a file
        now = utilities.getNow()
        t = utilities.getModificationFile(saveto)

        # Download a file
        if forcedownload or t + self._interval < now:
            print "Download %s feed [%s] %s" % (jobboardname, md5, url)
            if (not os.path.isdir(destdir)):
                os.makedirs(destdir)
                utilities.download_file(url, saveto)


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
        self.title = u""
        self.company = u""
        self.contract = u""
        self.location = u""
        self.salary = u""
        self.url = u""
        self.content = u""

    def load(self, src, ref, date_pub, date_add, title, company, contract, location, lat, lon, salary, url, content):

        self.src = src
        self.ref = ref

        self.date_pub = datetime.datetime.fromtimestamp(int(date_pub))
        self.date_add = datetime.datetime.fromtimestamp(int(date_add))
        self.title = title.encode("utf-8")
        self.company = company.encode("utf-8")
        self.contract = contract.encode("utf-8")
        self.location = location.encode("utf-8")
        self.salary = salary.encode("utf-8")
        self.url = url.encode("utf-8")
        self.content = content.encode("utf-8")

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

    def load_jobBoards(self):
        """ load all jobboards from jobboards directory
        """
        import glob
        import importlib

        fd = FeedDownloader('./dl')
        fd.configs = configs
        fd.downloads()
        sys.exit()

        for file in glob.glob("./jobboards/*.py"):
            name = os.path.splitext(os.path.basename(file))[0]
            if (name == '__init__'):
                continue

            module = importlib.import_module('jobboards.'+name);
            moduleClass = getattr(module, name)
            instance = moduleClass()
            self.jobBoardList.append(instance)

    def run(self):
        for item in self.jobBoardList:
            if not item.name in configs['global']['ignorefeeds']:
                print ""
                print "=================================="
                print item.name
                print "=================================="

                if configs['global']['debug']:
                    item.fetch()
                else:
                    try:
                        item.fetch()
                    except:
                        print "Ignored (parsing error)."

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
    parser.add_option('-b', '--blocklist',
                          action = 'store_true', dest = 'blocklist',
                          help = 'update blocklist')
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
        utilities.blacklist_flush()
        utilities.blocklist_load()
        bot = JobCatcher()
        bot.load_jobBoards()
        bot.run()
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
        bot = JobCatcher()
        bot.load_jobBoards()
        bot.run()
        sys.exit(0)

    if options.blocklist:
        utilities.blocklist_load();
        sys.exit(0)

    if options.flush:
        utilities.blacklist_flush()
        utilities.blocklist_load()
        sys.exit(0)
